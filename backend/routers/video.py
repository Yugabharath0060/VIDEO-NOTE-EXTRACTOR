"""
Video upload and processing router.
Handles local video file uploads and background processing.
"""
import os
import uuid
import asyncio
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.schemas import JobStatus, JobStatusResponse, VideoNotes
from config import UPLOADS_DIR, OUTPUTS_DIR, WHISPER_MODEL, MAX_UPLOAD_SIZE_BYTES

router = APIRouter(prefix="/api/video", tags=["video"])

# In-memory job store
jobs: dict = {}


def update_job(job_id: str, status: str = None, progress: int = None, message: str = None, result=None):
    if job_id not in jobs:
        jobs[job_id] = {}
    if status:
        jobs[job_id]["status"] = status
    if progress is not None:
        jobs[job_id]["progress"] = progress
    if message:
        jobs[job_id]["message"] = message
    if result:
        jobs[job_id]["result"] = result


def process_video_task(job_id: str, file_path: str, filename: str,
                       extract_audio: bool, extract_ocr: bool, generate_summary: bool):
    """Background task: full video processing pipeline."""
    from services.transcription import transcribe_video, get_full_text
    from services.ocr_service import extract_text_from_frames
    from services.summarizer import generate_summary as gen_summary

    try:
        title = os.path.splitext(filename)[0]
        transcript = []
        ocr_results = []
        summary = ""
        duration = None

        # Step 1: Transcription
        if extract_audio:
            update_job(job_id, progress=10, message="🎙️ Transcribing audio...")
            transcript = transcribe_video(file_path, WHISPER_MODEL)
            update_job(job_id, progress=50, message="✅ Transcription complete")

        # Step 2: OCR
        if extract_ocr:
            update_job(job_id, progress=55, message="🔍 Extracting text from frames...")
            ocr_results = extract_text_from_frames(file_path, frame_interval=60)
            update_job(job_id, progress=80, message="✅ OCR complete")

        # Step 3: Summarization
        if generate_summary and transcript:
            update_job(job_id, progress=82, message="🤖 Generating AI summary...")
            full_text = get_full_text(transcript)
            summary = gen_summary(transcript, full_text)
            update_job(job_id, progress=95, message="✅ Summary generated")

        # Get video duration
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frames / fps
            cap.release()
        except Exception:
            pass

        full_text = " ".join(seg.text for seg in transcript)
        result = VideoNotes(
            job_id=job_id,
            title=title,
            source=filename,
            duration=duration,
            transcript=transcript,
            ocr_texts=ocr_results,
            summary=summary,
            full_text=full_text
        )

        update_job(job_id, status="completed", progress=100, message="✅ Processing complete!", result=result.model_dump())

    except Exception as e:
        update_job(job_id, status="failed", message=f"❌ Error: {str(e)}")
        print(f"[Video] Processing failed for job {job_id}: {e}")


@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extract_audio: bool = True,
    extract_ocr: bool = True,
    generate_summary: bool = True
):
    """Upload a local video file and start processing."""
    allowed = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}
    ext = os.path.splitext(file.filename or "")[1].lower()

    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {', '.join(allowed)}")

    job_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(UPLOADS_DIR, f"{job_id}{ext}")

    # Save uploaded file
    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(413, "File too large")
        await f.write(content)

    update_job(job_id, status="processing", progress=5, message="📁 File uploaded, starting processing...")

    background_tasks.add_task(
        process_video_task, job_id, save_path, file.filename or "video",
        extract_audio, extract_ocr, generate_summary
    )

    return {"job_id": job_id, "message": "Processing started", "filename": file.filename}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check processing status for a job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]
