#!/usr/bin/env bash
# Build YouTube & SoundCloud Downloader for macOS.
# Run from project root. Requires: Python 3.9+, pip install -r requirements.txt pyinstaller
# Output: dist/YouTube Downloader (run with: ./dist/YouTube\ Downloader)

set -e
cd "$(dirname "$0")"

if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi

echo "Building executable..."
python3 -m PyInstaller --noconfirm downloader.spec

echo ""
echo "Done. Run: ./dist/YouTube\ Downloader"
echo "You need FFmpeg on PATH (brew install ffmpeg) unless you use the release build with bundled FFmpeg."
