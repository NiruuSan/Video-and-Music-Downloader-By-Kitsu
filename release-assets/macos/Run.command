#!/bin/bash
cd "$(dirname "$0")"

if [ ! -x "./YouTube Downloader" ]; then
  echo "YouTube Downloader not found in this folder."
  read -p "Press Enter to close..."
  exit 1
fi

echo "Starting YouTube & SoundCloud Downloader..."
echo "Your browser will open. Close this window to stop the app."
echo ""
./YouTube\ Downloader
read -p "Press Enter to close..."
