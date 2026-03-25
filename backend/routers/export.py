"""
Export router.
Handles exporting processed notes to PDF, Word, or Markdown.
"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models.schemas import ExportRequest
from config import OUTPUTS_DIR
from routers.video import jobs

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/")
async def export_notes(request: ExportRequest):
    """Export notes for a completed job."""
    job = jobs.get(request.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.get("status") != "completed":
        raise HTTPException(400, "Job is not yet completed")

    result_data = job.get("result")
    if not result_data:
        raise HTTPException(400, "No notes data available")

    from models.schemas import VideoNotes
    from services.exporter import export_notes as do_export

    notes = VideoNotes(**result_data)

    try:
        output_path = do_export(
            notes,
            OUTPUTS_DIR,
            request.format.value,
            include_timestamps=request.include_timestamps
        )
        return {
            "success": True,
            "download_url": f"/api/export/download/{request.job_id}/{request.format.value}",
            "filename": os.path.basename(output_path)
        }
    except Exception as e:
        raise HTTPException(500, f"Export failed: {str(e)}")


@router.get("/download/{job_id}/{fmt}")
async def download_export(job_id: str, fmt: str):
    """Download an exported file."""
    ext_map = {"pdf": ".pdf", "word": ".docx", "markdown": ".md"}
    ext = ext_map.get(fmt, ".md")

    # Find the file
    for f in os.listdir(OUTPUTS_DIR):
        if f.startswith(job_id) and f.endswith(ext):
            file_path = os.path.join(OUTPUTS_DIR, f)
            media_types = {
                ".pdf": "application/pdf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".md": "text/markdown"
            }
            return FileResponse(
                file_path,
                media_type=media_types.get(ext, "application/octet-stream"),
                filename=f
            )

    raise HTTPException(404, "Export file not found. Please export first.")
