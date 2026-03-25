"""
YouTube Service using yt-dlp.
Downloads audio/video from YouTube URLs for processing.
"""
import os
import yt_dlp
from typing import Optional, Dict


def get_video_info(url: str) -> Dict:
    """Fetch metadata from a YouTube URL without downloading."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Unknown"),
            "thumbnail": info.get("thumbnail", ""),
            "description": info.get("description", ""),
            "view_count": info.get("view_count", 0),
        }


def download_audio(url: str, output_dir: str, job_id: str) -> Optional[str]:
    """
    Download audio from YouTube URL and convert to WAV for Whisper.
    Returns path to downloaded audio file.
    """
    output_path = os.path.join(output_dir, f"{job_id}_audio.wav")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, f"{job_id}_audio.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    print(f"[YouTube] Downloading audio from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if os.path.exists(output_path):
        print(f"[YouTube] Audio saved to: {output_path}")
        return output_path

    # Try alternate extension
    for ext in ["wav", "mp3", "m4a", "webm"]:
        path = os.path.join(output_dir, f"{job_id}_audio.{ext}")
        if os.path.exists(path):
            return path

    return None


def download_video(url: str, output_dir: str, job_id: str) -> Optional[str]:
    """
    Download video from YouTube URL for OCR processing.
    Returns path to downloaded video file.
    """
    output_path = os.path.join(output_dir, f"{job_id}_video.mp4")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    print(f"[YouTube] Downloading video from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if os.path.exists(output_path):
        print(f"[YouTube] Video saved to: {output_path}")
        return output_path

    return None
