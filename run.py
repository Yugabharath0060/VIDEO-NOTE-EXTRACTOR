"""
One-click launcher for Video Note Extractor.
Run: python run.py
"""
import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Video Note Extractor — Launch Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                # Start web server (browser mode)
  python run.py --desktop      # Start desktop app (native window)
  python run.py --port 8080    # Use a custom port
        """
    )
    parser.add_argument("--desktop", action="store_true", help="Launch as desktop app (PyWebView)")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    # Update .env port if changed
    if args.port != 8000:
        os.environ["APP_PORT"] = str(args.port)

    if args.desktop:
        print("\n🖥️  Launching Desktop App...\n")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop"))
        from desktop.app import launch_desktop
        launch_desktop()
    else:
        print("\n🌐 Launching Web Server...\n")
        import subprocess
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", args.host,
            "--port", str(args.port),
            "--reload",
            "--log-level", "info"
        ], cwd=os.path.join(os.path.dirname(__file__), "backend"))


if __name__ == "__main__":
    print("=" * 55)
    print("  🎬 VideoNotes AI — Video Note Extractor v1.0")
    print("=" * 55)
    main()
