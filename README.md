# 🎬 VideoNotes AI — Video Note Extractor

> Extract notes from any video using AI transcription, OCR, and summarization.

![Tech Stack](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![Whisper](https://img.shields.io/badge/Whisper-OpenAI-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎙️ Speech Transcription | OpenAI Whisper (local, free) with timestamps |
| 🔍 OCR Extraction | Extract text from video frames using Tesseract |
| 🤖 AI Summarization | GPT-4o structured notes (or offline extractive fallback) |
| 📺 YouTube Support | Paste any YouTube URL to extract notes |
| ⏱️ Timestamps | Every note linked to exact video time |
| 📄 PDF Export | Styled PDF with ReportLab |
| 📝 Word Export | .docx with python-docx |
| #️⃣ Markdown Export | Clean markdown output |
| 🖥️ Desktop App | Native window using PyWebView |
| 🌐 Web App | Full browser UI |

---

## 📋 Prerequisites

Before running, ensure you have:

1. **Python 3.11+** — [Download](https://www.python.org/downloads/)
2. **FFmpeg** — Required by Whisper for audio processing
   - Windows: `winget install Gyan.FFmpeg` or [download here](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH
3. **Tesseract OCR** — Required for OCR feature
   - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - Default install path: `C:\Program Files\Tesseract-OCR\`
   - Add to system PATH

---

## 🚀 Installation & Setup

### Step 1: Clone / navigate to the project
```bash
cd video-note-extractor
```

### Step 2: Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux
```

### Step 3: Install dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Configure environment
Edit `.env` file (already created):
```env
OPENAI_API_KEY=sk-...     # Optional: for GPT-4o summaries
WHISPER_MODEL=base         # tiny | base | small | medium | large
```

### Step 5: Run the app

**Web Mode (browser):**
```bash
python run.py
# Then open: http://127.0.0.1:8000
```

**Desktop Mode (native window):**
```bash
# First install PyWebView
pip install pywebview

python run.py --desktop
```

**Direct backend start:**
```bash
cd backend
python main.py
```

---

## 📁 Project Structure

```
video-note-extractor/
├── backend/
│   ├── main.py                  # FastAPI app entry
│   ├── config.py                # Configuration
│   ├── services/
│   │   ├── transcription.py     # Whisper speech-to-text
│   │   ├── ocr_service.py       # Tesseract OCR
│   │   ├── youtube_service.py   # yt-dlp downloader
│   │   ├── summarizer.py        # AI summarization
│   │   └── exporter.py          # PDF/Word/MD export
│   ├── models/schemas.py        # Pydantic schemas
│   ├── routers/                 # API routes
│   ├── uploads/                 # Temp video storage
│   └── outputs/                 # Generated exports
├── frontend/
│   ├── index.html               # Main UI
│   ├── css/styles.css           # Premium dark theme
│   └── js/
│       ├── api.js               # API calls
│       ├── ui.js                # UI helpers
│       └── app.js               # Main app logic
├── desktop/
│   └── app.py                   # PyWebView launcher
├── run.py                       # One-click launcher
├── .env                         # Your configuration
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/video/upload` | Upload local video |
| `GET` | `/api/video/status/{job_id}` | Check processing status |
| `POST` | `/api/youtube/extract` | Extract from YouTube |
| `GET` | `/api/youtube/info?url=...` | Fetch YouTube metadata |
| `POST` | `/api/export/` | Generate export file |
| `GET` | `/api/export/download/{job_id}/{format}` | Download export |

Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ⚙️ Configuration Options

| Variable | Default | Options |
|----------|---------|---------|
| `OPENAI_API_KEY` | *(empty)* | Your OpenAI key |
| `WHISPER_MODEL` | `base` | `tiny`, `base`, `small`, `medium`, `large` |
| `APP_PORT` | `8000` | Any available port |
| `MAX_UPLOAD_SIZE_MB` | `500` | Any value in MB |

---

## 🧠 How It Works

```
Video/YouTube URL
       │
       ▼
  ┌─────────┐    ┌──────────────┐    ┌───────────┐
  │ Download │ ─► │  Transcribe  │ ─► │ Summarize │
  │ (yt-dlp) │    │  (Whisper)   │    │  (GPT-4o) │
  └─────────┘    └──────────────┘    └───────────┘
       │
       ▼
  ┌─────────┐
  │ Extract │
  │  Frames │ ─► OCR (Tesseract) ─► Text + Timestamps
  └─────────┘
       │
       ▼
  ┌──────────────────────────┐
  │  Export: PDF / Word / MD │
  └──────────────────────────┘
```

---

## 🐛 Troubleshooting

**Whisper model download fails:**
- Ensure you have internet connection on first run (model is ~74MB for `base`)

**FFmpeg not found:**
- Run `ffmpeg -version` to verify installation
- Re-add FFmpeg to your PATH and restart terminal

**Tesseract not found:**
- Run `tesseract --version` to verify
- Install from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH

**YouTube download fails:**
- Update yt-dlp: `pip install -U yt-dlp`

---

## 📄 License

MIT License — use freely for personal and commercial projects.
