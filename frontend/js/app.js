/**
 * Main Application Logic
 */

let selectedFile = null;
let currentJobId = null;
let pollInterval = null;
let ytDebounceTimer = null;

// ── File Handling ────────────────────────────────────────

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) setFile(file);
}

function handleDrop(event) {
  event.preventDefault();
  document.getElementById("upload-zone").classList.remove("drag-over");
  const file = event.dataTransfer.files[0];
  if (file) setFile(file);
}

function handleDragOver(event) {
  event.preventDefault();
  document.getElementById("upload-zone").classList.add("drag-over");
}

function handleDragLeave(event) {
  document.getElementById("upload-zone").classList.remove("drag-over");
}

function setFile(file) {
  const allowed = ["video/mp4", "video/avi", "video/quicktime", "video/x-msvideo",
                   "video/x-matroska", "video/webm", "video/x-flv", "video/x-ms-wmv", "video/mp4v-es"];
  const ext = file.name.split(".").pop().toLowerCase();
  const allowedExts = ["mp4", "avi", "mov", "mkv", "webm", "flv", "wmv", "m4v"];

  if (!allowedExts.includes(ext)) {
    showToast("⚠️ Unsupported file type. Please select a video file.", "error");
    return;
  }

  selectedFile = file;
  document.getElementById("file-name-display").textContent = file.name;
  document.getElementById("file-size-display").textContent = formatFileSize(file.size);
  document.getElementById("file-preview").classList.remove("hidden");
  document.getElementById("upload-zone").style.display = "none";
}

function clearFile() {
  selectedFile = null;
  document.getElementById("file-input").value = "";
  document.getElementById("file-preview").classList.add("hidden");
  document.getElementById("upload-zone").style.display = "";
}

// ── YouTube Preview ──────────────────────────────────────

function previewYoutube() {
  clearTimeout(ytDebounceTimer);
  const url = document.getElementById("youtube-url").value.trim();

  if (!url || (!url.includes("youtube.com") && !url.includes("youtu.be"))) {
    document.getElementById("yt-preview").classList.add("hidden");
    return;
  }

  ytDebounceTimer = setTimeout(async () => {
    try {
      // Extract thumbnail from YouTube URL without API call
      const videoId = extractYoutubeId(url);
      if (videoId) {
        document.getElementById("yt-thumb").src = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
        document.getElementById("yt-title-display").textContent = "Fetching video details...";
        document.getElementById("yt-duration-display").textContent = "";
        document.getElementById("yt-preview").classList.remove("hidden");

        // Fetch info from backend
        const info = await apiGetYoutubeInfo(url);
        document.getElementById("yt-title-display").textContent = info.title || "YouTube Video";
        document.getElementById("yt-duration-display").textContent =
          info.duration ? `⏱ ${formatDuration(info.duration)}` : "";
      }
    } catch (e) {
      // Silently fail preview
    }
  }, 800);
}

function extractYoutubeId(url) {
  const patterns = [
    /youtu\.be\/([^?&#]+)/,
    /youtube\.com\/watch\?v=([^&#]+)/,
    /youtube\.com\/embed\/([^?&#]+)/,
    /youtube\.com\/shorts\/([^?&#]+)/,
  ];
  for (const p of patterns) {
    const m = url.match(p);
    if (m) return m[1];
  }
  return null;
}

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    document.getElementById("youtube-url").value = text;
    previewYoutube();
    showToast("📋 Pasted from clipboard!", "info", 2000);
  } catch {
    showToast("⚠️ Could not access clipboard.", "error");
  }
}

// ── Extraction ───────────────────────────────────────────

async function startExtraction() {
  const activePanel = document.querySelector(".panel.active");
  const isYoutube = activePanel.id === "youtube-panel";

  const options = {
    audio: document.getElementById("opt-audio").checked,
    ocr: document.getElementById("opt-ocr").checked,
    summary: document.getElementById("opt-summary").checked,
  };

  if (!options.audio && !options.ocr) {
    showToast("⚠️ Please enable at least one extraction option.", "error");
    return;
  }

  if (isYoutube) {
    const url = document.getElementById("youtube-url").value.trim();
    if (!url) {
      showToast("⚠️ Please enter a YouTube URL.", "error");
      return;
    }
    if (!url.includes("youtube.com") && !url.includes("youtu.be")) {
      showToast("⚠️ Please enter a valid YouTube URL.", "error");
      return;
    }
    await startYoutubeExtraction(url, options);
  } else {
    if (!selectedFile) {
      showToast("⚠️ Please select a video file.", "error");
      return;
    }
    await startVideoUpload(options);
  }
}

async function startVideoUpload(options) {
  const btn = document.getElementById("extract-btn");
  btn.disabled = true;
  btn.querySelector(".btn-text").textContent = "Uploading...";

  showProgress();
  setProgress(5, "📁 Uploading video file...");

  try {
    const res = await apiUploadVideo(selectedFile, options);
    currentJobId = res.job_id;
    showToast(`✅ Upload complete! Processing job ${currentJobId}`, "success");
    startPolling(currentJobId);
  } catch (e) {
    showToast(`❌ ${e.message}`, "error");
    hideProgress();
    resetBtn();
  }
}

async function startYoutubeExtraction(url, options) {
  const btn = document.getElementById("extract-btn");
  btn.disabled = true;
  btn.querySelector(".btn-text").textContent = "Starting...";

  showProgress();
  setProgress(2, "🚀 Starting YouTube extraction...");

  try {
    const res = await apiExtractYoutube(url, options);
    currentJobId = res.job_id;
    showToast("✅ YouTube extraction started!", "success");
    startPolling(currentJobId);
  } catch (e) {
    showToast(`❌ ${e.message}`, "error");
    hideProgress();
    resetBtn();
  }
}

// ── Polling ──────────────────────────────────────────────

function startPolling(jobId) {
  clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    try {
      const status = await apiGetStatus(jobId);
      setProgress(status.progress || 0, status.message || "Processing...");

      if (status.status === "completed") {
        clearInterval(pollInterval);
        setProgress(100, "✅ Done!");
        setTimeout(() => {
          hideProgress();
          renderResults(status.result);
          resetBtn();
          showToast("🎉 Notes extracted successfully!", "success");
        }, 600);
      } else if (status.status === "failed") {
        clearInterval(pollInterval);
        hideProgress();
        resetBtn();
        showToast(`❌ ${status.message}`, "error");
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 2000);
}

// ── Export ───────────────────────────────────────────────

async function exportNotes(format) {
  if (!currentJobId) {
    showToast("⚠️ No job to export.", "error");
    return;
  }

  const includeTimestamps = document.getElementById("exp-timestamps").checked;
  const statusEl = document.getElementById("export-status");
  const btn = document.getElementById(`exp-${format === "markdown" ? "md" : format}`);

  btn.disabled = true;
  statusEl.textContent = `⏳ Generating ${format.toUpperCase()} export...`;

  try {
    await apiExport(currentJobId, format, includeTimestamps);
    await apiDownload(currentJobId, format);
    statusEl.textContent = `✅ ${format.toUpperCase()} downloaded successfully!`;
    showToast(`📄 ${format.toUpperCase()} export downloaded!`, "success");
  } catch (e) {
    statusEl.textContent = `❌ Export failed: ${e.message}`;
    showToast(`❌ Export failed: ${e.message}`, "error");
  } finally {
    btn.disabled = false;
  }
}

// ── Utilities ─────────────────────────────────────────────

function resetBtn() {
  const btn = document.getElementById("extract-btn");
  btn.disabled = false;
  btn.querySelector(".btn-text").textContent = "Extract Notes";
}

function resetApp() {
  clearInterval(pollInterval);
  currentJobId = null;
  clearFile();
  document.getElementById("youtube-url").value = "";
  document.getElementById("yt-preview").classList.add("hidden");
  document.getElementById("results-card").classList.add("hidden");
  document.getElementById("progress-card").classList.add("hidden");
  document.getElementById("export-status").textContent = "";
  resetBtn();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Check Backend Health ──────────────────────────────────

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error();
    document.querySelector(".nav-badge span:last-child").textContent = "Backend Online";
    document.querySelector(".badge-dot").style.background = "var(--green)";
  } catch {
    document.querySelector(".nav-badge span:last-child").textContent = "Backend Offline";
    document.querySelector(".badge-dot").style.background = "#ef4444";
    showToast("⚠️ Backend is offline. Please start the server.", "error", 8000);
  }
}

// Init
document.addEventListener("DOMContentLoaded", checkHealth);
