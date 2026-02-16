#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  FFmpeg installer for YouTube Downloader"
echo "=========================================="
echo ""

if ! command -v brew &>/dev/null; then
  echo "Homebrew is not installed."
  echo "Install it from https://brew.sh"
  echo ""
  echo "Or run this in Terminal:"
  echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo ""
  read -p "Press Enter to close..."
  exit 1
fi

echo "Installing FFmpeg (required for the downloader)..."
echo ""
if brew install ffmpeg; then
  echo ""
  echo "Done! You can now double-click Run.command to start the app."
else
  echo ""
  echo "Installation failed. Try running in Terminal: brew install ffmpeg"
fi
echo ""
read -p "Press Enter to close..."
