#!/usr/bin/env bash
# Build a GitHub-release-ready folder for macOS: app + bundled FFmpeg.
# Run from project root. Requires: Python 3.9+, pip install -r requirements.txt pyinstaller
# Output: release/YouTube Downloader/ (zip this and upload to GitHub Releases for macOS)

set -e
cd "$(dirname "$0")"

if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi

RELEASE_DIR="release/YouTube Downloader"
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
  FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-macosarm64-gpl.zip"
  FFMPEG_DIR_NAME="ffmpeg-master-latest-macosarm64-gpl"
else
  FFMPEG_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-macos64-gpl.zip"
  FFMPEG_DIR_NAME="ffmpeg-master-latest-macos64-gpl"
fi

echo "[1/4] Building executable..."
python3 -m PyInstaller --noconfirm downloader.spec

echo "[2/4] Creating release folder..."
rm -rf release
mkdir -p "$RELEASE_DIR"
cp "dist/YouTube Downloader" "$RELEASE_DIR/YouTube Downloader"
chmod +x "$RELEASE_DIR/YouTube Downloader"

echo "[3/4] Downloading FFmpeg for macOS ($ARCH)..."
curl -sL -o "release/ffmpeg.zip" "$FFMPEG_URL" || {
  echo "Failed to download FFmpeg. Create $RELEASE_DIR/ffmpeg and add ffmpeg + ffprobe binaries, then zip $RELEASE_DIR"
  exit 1
}

echo "[4/4] Extracting FFmpeg..."
mkdir -p "$RELEASE_DIR/ffmpeg"
unzip -q -o release/ffmpeg.zip -d release
if [ -d "release/$FFMPEG_DIR_NAME/bin" ]; then
  cp "release/$FFMPEG_DIR_NAME/bin/ffmpeg" "$RELEASE_DIR/ffmpeg/"
  cp "release/$FFMPEG_DIR_NAME/bin/ffprobe" "$RELEASE_DIR/ffmpeg/"
  chmod +x "$RELEASE_DIR/ffmpeg/ffmpeg" "$RELEASE_DIR/ffmpeg/ffprobe"
  rm -rf "release/$FFMPEG_DIR_NAME"
fi
rm -f release/ffmpeg.zip

echo ""
echo "Done. Release folder: $RELEASE_DIR"
echo "  - YouTube Downloader"
echo "  - ffmpeg/ffmpeg, ffmpeg/ffprobe"
echo ""
echo "Zip the folder and upload to GitHub Releases (e.g. YouTube-Downloader-macos-arm64.zip or macos-x64.zip)."
