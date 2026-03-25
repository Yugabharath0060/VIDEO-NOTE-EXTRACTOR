from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from enum import Enum


class ExportFormat(str, Enum):
    pdf = "pdf"
    word = "word"
    markdown = "markdown"


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class YouTubeRequest(BaseModel):
    url: str
    extract_audio: bool = True
    extract_ocr: bool = True
    generate_summary: bool = True


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class OCRResult(BaseModel):
    timestamp: float
    frame_number: int
    text: str


class VideoNotes(BaseModel):
    job_id: str
    title: str
    source: str
    duration: Optional[float] = None
    transcript: List[TranscriptSegment] = []
    ocr_texts: List[OCRResult] = []
    summary: Optional[str] = None
    full_text: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = 0
    message: str = ""
    result: Optional[VideoNotes] = None


class ExportRequest(BaseModel):
    job_id: str
    format: ExportFormat
    include_transcript: bool = True
    include_ocr: bool = True
    include_summary: bool = True
    include_timestamps: bool = True
