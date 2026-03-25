/**
 * API Communication Layer
 * All calls to the FastAPI backend.
 */

const API_BASE = "http://127.0.0.1:8000";

async function apiUploadVideo(file, options) {
  const formData = new FormData();
  formData.append("file", file);
  const params = new URLSearchParams({
    extract_audio: options.audio,
    extract_ocr: options.ocr,
    generate_summary: options.summary,
  });
  const res = await fetch(`${API_BASE}/api/video/upload?${params}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

async function apiExtractYoutube(url, options) {
  const res = await fetch(`${API_BASE}/api/youtube/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      extract_audio: options.audio,
      extract_ocr: options.ocr,
      generate_summary: options.summary,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `YouTube extraction failed (${res.status})`);
  }
  return res.json();
}

async function apiGetStatus(jobId) {
  const res = await fetch(`${API_BASE}/api/video/status/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

async function apiGetYoutubeInfo(url) {
  const res = await fetch(`${API_BASE}/api/youtube/info?url=${encodeURIComponent(url)}`);
  if (!res.ok) throw new Error("Failed to fetch YouTube info");
  return res.json();
}

async function apiExport(jobId, format, includeTimestamps) {
  const res = await fetch(`${API_BASE}/api/export/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_id: jobId,
      format,
      include_timestamps: includeTimestamps,
      include_transcript: true,
      include_ocr: true,
      include_summary: true,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Export failed");
  }
  return res.json();
}

async function apiDownload(jobId, format) {
  const url = `${API_BASE}/api/export/download/${jobId}/${format}`;
  const link = document.createElement("a");
  link.href = url;
  link.download = "";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
