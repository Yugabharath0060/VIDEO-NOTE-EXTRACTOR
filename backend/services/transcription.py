"""
Transcription Service using OpenAI Whisper (runs locally, free).
Converts audio/video to timestamped text.
"""
import os
import whisper
from typing import List
from ..models.schemas import TranscriptSegment


_model = None


def get_model(model_name: str = "base"):
    """Load Whisper model (cached after first load)."""
    global _model
    if _model is None:
        print(f"[Transcription] Loading Whisper model: {model_name}")
        _model = whisper.load_model(model_name)
        print("[Transcription] Model loaded successfully.")
    return _model


def transcribe_video(file_path: str, model_name: str = "base") -> List[TranscriptSegment]:
    """
    Transcribe audio from a video/audio file using Whisper.
    Returns a list of transcript segments with timestamps.
    """
    model = get_model(model_name)
    print(f"[Transcription] Transcribing: {file_path}")

    result = model.transcribe(
        file_path,
        verbose=False,
        word_timestamps=True,
        task="transcribe"
    )

    segments = []
    for seg in result.get("segments", []):
        segments.append(TranscriptSegment(
            start=round(seg["start"], 2),
            end=round(seg["end"], 2),
            text=seg["text"].strip()
        ))

    print(f"[Transcription] Extracted {len(segments)} segments.")
    return segments


def get_full_text(segments: List[TranscriptSegment]) -> str:
    """Combine all transcript segments into full text."""
    return " ".join(seg.text for seg in segments)
