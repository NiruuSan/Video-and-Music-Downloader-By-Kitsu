# YouTube & SoundCloud Downloader

Download **YouTube** videos as MP4 or MP3 (including 4K/1440p), and **SoundCloud** tracks or full **playlists** (all tracks + cover art + playlist info in a zip). No account needed.

---

## For users

**Windows**
1. Download the latest **Windows** zip from [Releases](https://github.com/NiruuSan/Video-and-Music-Downloader-By-Kitsu/releases).
2. Unzip anywhere, then double-click **YouTube Downloader.exe**. Your browser will open.

**macOS**
1. Download the **macOS** zip (e.g. `YouTube-Downloader-macos-arm64.zip` for Apple Silicon, or `macos-x64.zip` for Intel).
2. Unzip, open **Terminal**, then run: `cd /path/to/YouTube\ Downloader` and `./YouTube\ Downloader`. Your browser will open.

**Then (both):** Choose YouTube or SoundCloud, paste a URL, set options, click Download. For SoundCloud playlists, check “Download as playlist” to get a zip with all tracks, cover art, and playlist info. Close the console/Terminal window to stop the app. Downloads go to your browser’s download folder.

**Included:** FFmpeg is bundled in the zip, so you don’t need to install it.

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
