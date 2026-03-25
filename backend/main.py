"""
Video Note Extractor — FastAPI Backend
Main application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import APP_HOST, APP_PORT, DEBUG, FRONTEND_DIR
from routers import video, youtube, export

# ─── App Setup ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Video Note Extractor API",
    description="Extract notes from videos using AI transcription, OCR, and summarization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — allow all origins in dev mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ────────────────────────────────────────────────────────────────
app.include_router(video.router)
app.include_router(youtube.router)
app.include_router(export.router)

# ─── Health Check ───────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Video Note Extractor", "version": "1.0.0"}

# ─── Serve Frontend ─────────────────────────────────────────────────────────
frontend_path = os.path.abspath(FRONTEND_DIR)

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🎬 Video Note Extractor")
    print(f"   Backend: http://{APP_HOST}:{APP_PORT}")
    print(f"   API Docs: http://{APP_HOST}:{APP_PORT}/docs")
    print(f"   Frontend: http://{APP_HOST}:{APP_PORT}/")
    print("=" * 60)
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level="info"
    )
