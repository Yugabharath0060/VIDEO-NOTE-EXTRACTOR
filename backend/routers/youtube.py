"""
YouTube router.
Handles YouTube URL extraction and processing.
"""
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.schemas import YouTubeRequest
from config import UPLOADS_DIR, WHISPER_MODEL
from routers.video import jobs, update_job

router = APIRouter(prefix="/api/youtube", tags=["youtube"])


def process_youtube_task(job_id: str, url: str, extract_audio: bool, extract_ocr: bool, generate_summary: bool):
    """Background task: download and process YouTube video."""
    from services.youtube_service import get_video_info, download_audio, download_video
    from services.transcription import transcribe_video, get_full_text
    from services.ocr_service import extract_text_from_frames
    from services.summarizer import generate_summary as gen_summary
    from models.schemas import VideoNotes

    try:
        # Step 1: Fetch video info
        update_job(job_id, progress=5, message="📡 Fetching video info...")
        info = get_video_info(url)
        title = info.get("title", "YouTube Video")
        duration = info.get("duration", None)

        transcript = []
        ocr_results = []
        summary = ""
        audio_path = None
        video_path = None

        # Step 2: Download audio for transcription
        if extract_audio:
            update_job(job_id, progress=15, message="⬇️ Downloading audio...")
            audio_path = download_audio(url, UPLOADS_DIR, job_id)
            if not audio_path:
                raise Exception("Failed to download audio")
            update_job(job_id, progress=35, message="🎙️ Transcribing audio...")
            transcript = transcribe_video(audio_path, WHISPER_MODEL)
            update_job(job_id, progress=65, message="✅ Transcription complete")

        # Step 3: Download video for OCR
        if extract_ocr:
            update_job(job_id, progress=67, message="⬇️ Downloading video for OCR...")
            video_path = download_video(url, UPLOADS_DIR, job_id)
            if video_path:
                update_job(job_id, progress=70, message="🔍 Extracting text from frames...")
                ocr_results = extract_text_from_frames(video_path, frame_interval=90)
                update_job(job_id, progress=88, message="✅ OCR complete")

        # Step 4: Summarize
        if generate_summary and transcript:
            update_job(job_id, progress=90, message="🤖 Generating AI summary...")
            full_text = get_full_text(transcript)
            summary = gen_summary(transcript, full_text)
            update_job(job_id, progress=97, message="✅ Summary generated")

        full_text = " ".join(seg.text for seg in transcript)
        result = VideoNotes(
            job_id=job_id,
            title=title,
            source=url,
            duration=duration,
            transcript=transcript,
            ocr_texts=ocr_results,
            summary=summary,
            full_text=full_text
        )

        update_job(job_id, status="completed", progress=100, message="✅ Processing complete!", result=result.model_dump())

    except Exception as e:
        update_job(job_id, status="failed", message=f"❌ Error: {str(e)}")
        print(f"[YouTube] Processing failed for job {job_id}: {e}")


@router.post("/extract")
async def extract_from_youtube(request: YouTubeRequest, background_tasks: BackgroundTasks):
    """Start YouTube video extraction."""
    if "youtube.com" not in request.url and "youtu.be" not in request.url:
        raise HTTPException(400, "Please provide a valid YouTube URL")

    job_id = str(uuid.uuid4())[:8]
    update_job(job_id, status="processing", progress=2, message="🚀 Starting YouTube extraction...")

    background_tasks.add_task(
        process_youtube_task, job_id, request.url,
        request.extract_audio, request.extract_ocr, request.generate_summary
    )

    return {"job_id": job_id, "message": "YouTube processing started", "url": request.url}


@router.get("/info")
async def get_youtube_info(url: str):
    """Fetch YouTube video metadata without downloading."""
    try:
        from services.youtube_service import get_video_info
        info = get_video_info(url)
        return info
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch video info: {str(e)}")
