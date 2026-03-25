"""
OCR Service using OpenCV + Tesseract.
Extracts text visible in video frames (slides, screen recordings, whiteboards, etc.).
"""
import cv2
import pytesseract
from PIL import Image
import numpy as np
from typing import List
from ..models.schemas import OCRResult


def extract_text_from_frames(
    video_path: str,
    frame_interval: int = 30,
    min_confidence: float = 60.0,
    progress_callback=None
) -> List[OCRResult]:
    """
    Extract text from video frames using OCR.

    Args:
        video_path: Path to video file
        frame_interval: Extract every N frames (default: every 30 frames ~= 1s at 30fps)
        min_confidence: Minimum OCR confidence to include text
        progress_callback: Optional callback(percent) for progress updates

    Returns:
        List of OCRResult with timestamps and extracted text
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[OCR] Failed to open video: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    results: List[OCRResult] = []
    seen_texts = set()
    frame_number = 0

    print(f"[OCR] Processing video: {total_frames} frames at {fps:.1f} FPS")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % frame_interval == 0:
            timestamp = frame_number / fps

            # Preprocess for better OCR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # OCR with confidence data
            pil_img = Image.fromarray(thresh)
            data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)

            # Collect words above confidence threshold
            words = []
            for i, conf in enumerate(data["conf"]):
                try:
                    if float(conf) >= min_confidence:
                        word = data["text"][i].strip()
                        if word:
                            words.append(word)
                except (ValueError, TypeError):
                    continue

            text = " ".join(words).strip()

            # Only add if text is meaningful and not duplicate
            if text and len(text) > 10 and text not in seen_texts:
                seen_texts.add(text)
                results.append(OCRResult(
                    timestamp=round(timestamp, 2),
                    frame_number=frame_number,
                    text=text
                ))

            if progress_callback and total_frames > 0:
                progress_callback(int((frame_number / total_frames) * 100))

        frame_number += 1

    cap.release()
    print(f"[OCR] Extracted {len(results)} unique text blocks.")
    return results
