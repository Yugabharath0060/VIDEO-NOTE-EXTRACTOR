"""
Summarizer Service.
Uses OpenAI GPT-4o if API key is available, otherwise falls back to extractive summarization.
"""
import os
from typing import List, Optional
from ..models.schemas import TranscriptSegment
from ..config import OPENAI_API_KEY


def summarize_with_openai(text: str) -> str:
    """Generate AI summary using OpenAI GPT-4o."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""You are a note-taking assistant. Analyze the following video transcript and generate clear, structured notes.

Format your output as:
## 📋 Key Topics
- Bullet points of main topics

## 💡 Key Points
- Important facts and insights

## 🔑 Summary
A concise 2-3 paragraph summary

## ✅ Action Items / Takeaways
- Any actionable points mentioned

Transcript:
{text[:8000]}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert note-taking assistant that creates clear, structured notes from video transcripts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.3
    )

    return response.choices[0].message.content


def summarize_extractive(text: str, num_sentences: int = 10) -> str:
    """
    Simple extractive summarization (no API required).
    Picks the most important sentences based on word frequency.
    """
    import re
    from collections import Counter

    # Clean text
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return text

    # Word frequency scoring
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "has", "her", "was", "one", "our", "out", "day", "get", "has",
        "him", "his", "how", "its", "may", "new", "now", "old", "see",
        "two", "who", "boy", "did", "she", "use", "way", "this", "that",
        "with", "have", "from", "they", "will", "been", "said", "each",
        "which", "their", "there", "what", "about", "would", "make",
        "like", "into", "than", "time", "very", "when", "come", "your",
        "just", "than"
    }
    word_freq = Counter(w for w in words if w not in stop_words)

    # Score sentences
    scored = []
    for sent in sentences:
        score = sum(word_freq.get(w.lower(), 0) for w in re.findall(r'\b[a-zA-Z]{3,}\b', sent))
        scored.append((score, sent))

    # Take top sentences, preserve order
    top_indices = sorted(
        range(len(scored)),
        key=lambda i: scored[i][0],
        reverse=True
    )[:num_sentences]
    top_indices.sort()

    summary_sentences = [scored[i][1] for i in top_indices]
    summary = " ".join(summary_sentences)

    return f"""## 📋 Auto-Generated Summary
*(AI summarization unavailable — add OPENAI_API_KEY for better summaries)*

{summary}

---
**Total transcript length:** {len(text.split())} words
"""


def generate_summary(segments: List[TranscriptSegment], full_text: Optional[str] = None) -> str:
    """
    Generate a summary from transcript segments.
    Uses OpenAI if API key is set, else falls back to extractive summarization.
    """
    text = full_text or " ".join(seg.text for seg in segments)

    if not text.strip():
        return "No transcript content available for summarization."

    if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        try:
            print("[Summarizer] Using OpenAI GPT-4o...")
            return summarize_with_openai(text)
        except Exception as e:
            print(f"[Summarizer] OpenAI failed: {e}. Falling back to extractive.")

    print("[Summarizer] Using extractive summarization...")
    return summarize_extractive(text)
