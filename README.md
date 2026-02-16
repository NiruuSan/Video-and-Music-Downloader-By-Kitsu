# YouTube & SoundCloud Downloader

Download **YouTube** videos as MP4 or MP3 (including 4K/1440p), and **SoundCloud** tracks or full **playlists** (all tracks + cover art + playlist info in a zip). No account needed.

---

## For users

**Windows**
1. Download the latest **Windows** zip from [Releases](https://drive.google.com/file/d/17aiTdKpeMweVwArd-4_cFr8D3vbUjtvx/view?usp=sharing).
2. Unzip anywhere, then double-click **YouTube Downloader.exe**. Your browser will open.

**macOS**
1. Download the **macOS** zip from [Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases).
2. Unzip and open **Installation.txt** for full instructions. In short: double-click **install_ffmpeg.command** (installs FFmpeg via Homebrew), then double-click **Run.command** to start the app. Your browser will open.

**Then (both):** Choose YouTube or SoundCloud, paste a URL, set options, click Download. For SoundCloud playlists, check “Download as playlist” to get a zip with all tracks, cover art, and playlist info. Close the console/Terminal window to stop the app. Downloads go to your browser’s download folder.

**Note:** Windows zip includes FFmpeg. macOS zip includes **Installation.txt** and **install_ffmpeg.command** (double-click to install FFmpeg) and **Run.command** (double-click to run the app).

---

## For developers (build from source)

### Requirements

- **Python 3.9+**
- **FFmpeg** on PATH (for running with `python app.py`)  
  - [Download FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.

### Run with Python

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

### Build the executable (for yourself)

**Windows**
```batch
pip install -r requirements.txt pyinstaller
build.bat
```
Run **`dist\YouTube Downloader.exe`**.

**macOS**
```bash
pip install -r requirements.txt pyinstaller
chmod +x build.sh && ./build.sh
```
Run **`./dist/YouTube\ Downloader`**. You need FFmpeg on PATH (`brew install ffmpeg`) unless you use the release build below.

### Build a release package for GitHub (app + bundled FFmpeg)

Creates a folder with the app and FFmpeg so users need no setup.

**Windows**
```batch
build_release.bat
```
Produces **`release\YouTube Downloader\`** with `YouTube Downloader.exe` and `ffmpeg\`. Zip it and upload as e.g. `YouTube-Downloader-win64.zip`.

**macOS** (run on a Mac)
```bash
chmod +x build_release.sh && ./build_release.sh
```
Produces **`release/YouTube Downloader/`** with `YouTube Downloader` and `ffmpeg/` (Intel or Apple Silicon based on your Mac). Zip it and upload as e.g. `YouTube-Downloader-macos-arm64.zip` or `macos-x64.zip`.

**No Mac?** If you’re on Windows only, you can still ship a macOS build: push the repo (including the `.github/workflows/release.yml` file) to GitHub. When you **publish a Release** (Releases → Create new release → Publish), GitHub Actions will build both **Windows** and **macOS** and attach `YouTube-Downloader-win64.zip` and `YouTube-Downloader-macos.zip` to that release. You don’t need to run `build_release.sh` locally.

---

## Supported URLs

**YouTube:** `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`

**SoundCloud:** any track or playlist/set URL, e.g. `soundcloud.com/artist/track-name`, `soundcloud.com/artist/sets/playlist-name`

## Notes

- **YouTube:** MP4 (best video+audio, 4K/1440p/1080p/…) or MP3 (best/320/192/128 kbps).
- **SoundCloud:** MP3 only. Single track or full playlist (zip with tracks + cover.jpg + playlist.txt).
- FFmpeg is required for MP4 and for SoundCloud/MP3 conversion. Everything runs on your machine (Windows or macOS).
