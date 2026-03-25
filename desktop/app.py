"""
Desktop App Launcher using PyWebView.
Wraps the web frontend in a native desktop window.
"""
import sys
import os
import threading
import time
import webbrowser

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def start_backend():
    """Start the FastAPI backend server in a background thread."""
    import uvicorn
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        reload=False
    )


def wait_for_backend(max_wait: int = 30):
    """Wait until the backend server is ready."""
    import urllib.request
    for _ in range(max_wait * 2):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def launch_desktop():
    """Launch the app as a desktop window using PyWebView."""
    try:
        import webview

        # Start backend in background
        print("[Desktop] Starting backend server...")
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()

        # Wait for backend
        print("[Desktop] Waiting for backend to start...")
        if wait_for_backend():
            print("[Desktop] Backend is ready!")
        else:
            print("[Desktop] Backend took too long. Opening anyway...")

        # Create desktop window
        window = webview.create_window(
            title="VideoNotes AI — Video Note Extractor",
            url="http://127.0.0.1:8000/",
            width=1280,
            height=800,
            min_size=(900, 600),
            resizable=True,
            on_top=False,
            confirm_close=False,
            background_color="#080c14",
        )
        webview.start(debug=False)

    except ImportError:
        print("[Desktop] PyWebView not installed. Opening in browser instead...")
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        if wait_for_backend():
            webbrowser.open("http://127.0.0.1:8000/")
            print("[Desktop] Opened in browser. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[Desktop] Shutting down.")


if __name__ == "__main__":
    print("=" * 55)
    print("   🎬 VideoNotes AI — Desktop Edition")
    print("=" * 55)
    launch_desktop()
