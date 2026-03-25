/**
 * UI Helper Functions
 */

function showToast(message, type = "info", duration = 4000) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), duration);
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
}

function formatTimestamp(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return [h, m, s].map(v => String(v).padStart(2, "0")).join(":");
}

function formatDuration(seconds) {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.getElementById(`${tab}-tab`).classList.add("active");
  document.getElementById(`${tab}-panel`).classList.add("active");
}

function switchResultTab(tab) {
  document.querySelectorAll(".result-tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".result-tab-content").forEach(c => c.classList.remove("active"));
  document.getElementById(`rt-${tab}`).classList.add("active");
  document.getElementById(`tab-${tab}`).classList.add("active");
}

function setProgress(percent, message) {
  document.getElementById("progress-bar").style.width = `${percent}%`;
  if (message) document.getElementById("progress-message").textContent = message;

  // Activate steps
  const steps = {
    "step-upload":    percent >= 5,
    "step-transcribe": percent >= 20,
    "step-ocr":       percent >= 55,
    "step-summary":   percent >= 82,
    "step-done":      percent >= 100,
  };
  for (const [id, active] of Object.entries(steps)) {
    document.getElementById(id).dataset.active = active;
  }
}

function showProgress() {
  document.getElementById("progress-card").classList.remove("hidden");
  document.getElementById("results-card").classList.add("hidden");
}

function hideProgress() {
  document.getElementById("progress-card").classList.add("hidden");
}

function parseMarkdownNotes(md) {
  if (!md) return "<em>No summary available.</em>";
  return md
    .replace(/^## (.*)/gm, '<h2>$1</h2>')
    .replace(/^- (.*)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/gs, '<ul>$&</ul>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^(?!<h2|<ul|<li)(.*)/gm, (m, p) => p.trim() ? `<p>${p}</p>` : '')
    .replace(/\n{2,}/g, '');
}

function renderResults(data) {
  const { title, source, duration, transcript, ocr_texts, summary, job_id } = data;

  document.getElementById("result-title").textContent = title || "Video Notes";
  document.getElementById("result-meta").textContent =
    [source, duration ? formatDuration(duration) : null].filter(Boolean).join(" · ");

  // Summary
  const summaryEl = document.getElementById("summary-content");
  summaryEl.innerHTML = summary ? parseMarkdownNotes(summary) : "<em>No summary generated.</em>";

  // Transcript
  const transcriptEl = document.getElementById("transcript-content");
  if (transcript && transcript.length > 0) {
    transcriptEl.innerHTML = transcript.map(seg => `
      <div class="transcript-seg">
        <span class="seg-time">${formatTimestamp(seg.start)}</span>
        <span class="seg-text">${seg.text}</span>
      </div>
    `).join("");
  } else {
    transcriptEl.innerHTML = "<em>No transcript available.</em>";
  }

  // OCR
  const ocrEl = document.getElementById("ocr-content");
  if (ocr_texts && ocr_texts.length > 0) {
    ocrEl.innerHTML = ocr_texts.map(item => `
      <div class="ocr-item">
        <div class="ocr-time">⏱ ${formatTimestamp(item.timestamp)}</div>
        <div class="ocr-text">${item.text}</div>
      </div>
    `).join("");
  } else {
    ocrEl.innerHTML = "<em>No on-screen text detected.</em>";
  }

  document.getElementById("results-card").classList.remove("hidden");
  document.getElementById("results-card").scrollIntoView({ behavior: "smooth", block: "start" });
}

function scrollToApp() {
  document.getElementById("app").scrollIntoView({ behavior: "smooth", block: "start" });
}
