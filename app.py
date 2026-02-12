"""
YouTube & SoundCloud Downloader - Flask backend.
Uses yt-dlp for highest quality MP4/MP3 (YouTube) and MP3 (SoundCloud).
Runnable as script or as PyInstaller executable (double-click to start).
"""
import io
import os
import re
import sys
import time
import uuid
import webbrowser
import zipfile
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request

from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL

# Support running as frozen exe (PyInstaller)
if getattr(sys, "frozen", False):
    _BASE_DIR = Path(sys._MEIPASS)
    _APP_DIR = Path(sys.executable).resolve().parent
else:
    _BASE_DIR = Path(__file__).resolve().parent
    _APP_DIR = _BASE_DIR

DOWNLOAD_FOLDER = _APP_DIR / "downloads"
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Optional bundled FFmpeg (next to app in release builds)
FFMPEG_DIR = _APP_DIR / "ffmpeg"
_FFMPEG_LOCATION = None
if getattr(sys, "frozen", False):
    _ffmpeg_name = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    if (FFMPEG_DIR / _ffmpeg_name).exists():
        _FFMPEG_LOCATION = str(FFMPEG_DIR)

app = Flask(__name__, static_folder=None, template_folder=str(_BASE_DIR / "templates"))
app.config["DOWNLOAD_FOLDER"] = str(DOWNLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024  # 4 KB max for request body

# Allow common YouTube URL patterns
YOUTUBE_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)[\w-]+"
)

# SoundCloud: track, playlist/set, user stream
SOUNDCLOUD_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?soundcloud\.com/[\w\-./]+",
    re.IGNORECASE,
)


def is_youtube_url(url: str) -> bool:
    return bool(url and YOUTUBE_PATTERN.match(url.strip()))


def is_soundcloud_url(url: str) -> bool:
    return bool(url and SOUNDCLOUD_PATTERN.match(url.strip()))


def is_soundcloud_playlist(url: str) -> bool:
    if not is_soundcloud_url(url):
        return False
    u = url.strip().lower()
    return "/sets/" in u or "?in=" in u


# MP4 quality: format selector for max resolution.
# 4K/1440p: no [ext=mp4] on video so we get VP9/AV1 when that's the only option; FFmpeg merges to mp4.
MP4_QUALITY_FORMATS = {
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    "2160": "bestvideo[height<=2160]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best",
    "1440": "bestvideo[height<=1440]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best",
    "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
    "720": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
    "480": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
    "360": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best",
}

# MP3 quality: bitrate in kbps, or "0" for best VBR
MP3_QUALITY_BITRATE = frozenset({"best", "320", "192", "128"})


def _base_ydl_opts(out_path: str) -> dict:
    opts = {"outtmpl": out_path, "quiet": True, "no_warnings": True}
    if _FFMPEG_LOCATION:
        opts["ffmpeg_location"] = _FFMPEG_LOCATION
    return opts


def get_ydl_opts_mp4(out_path: str, quality: str = "best") -> dict:
    """MP4: best video + best audio, merged. Quality limits max resolution."""
    fmt = MP4_QUALITY_FORMATS.get(quality, MP4_QUALITY_FORMATS["best"])
    opts = _base_ydl_opts(out_path)
    opts["format"] = fmt
    opts["merge_output_format"] = "mp4"
    return opts


def get_ydl_opts_audio(out_path: str, audio_format: str = "mp3", quality: str = "best") -> dict:
    """Best audio, convert to MP3 or WAV. audio_format: 'mp3' or 'wav'. Quality only applies to MP3."""
    pp = {
        "key": "FFmpegExtractAudio",
        "preferredcodec": audio_format if audio_format == "wav" else "mp3",
    }
    if audio_format == "mp3":
        if quality == "best" or quality not in MP3_QUALITY_BITRATE:
            pp["preferredquality"] = "0"
        else:
            pp["postprocessor_args"] = ["-b:a", f"{quality}k"]
    opts = _base_ydl_opts(out_path)
    opts["format"] = "bestaudio/best"
    opts["postprocessors"] = [pp]
    return opts


def get_ydl_opts_mp3(out_path: str, quality: str = "best") -> dict:
    """MP3: best audio, then convert to MP3. Quality = bitrate or best."""
    return get_ydl_opts_audio(out_path, "mp3", quality)


def get_ydl_opts_soundcloud(out_path: str, quality: str = "best", audio_format: str = "mp3") -> dict:
    """SoundCloud: best audio, convert to MP3 or WAV."""
    return get_ydl_opts_audio(out_path, audio_format, quality)


def _sanitize_filename(s: str, max_len: int = 120) -> str:
    return re.sub(r'[<>:"/\\|?*]', "", (s or "").strip())[:max_len]


@app.route("/")
def index():
    path = _BASE_DIR / "templates" / "index.html"
    return send_file(str(path))


def _fetch_cover_image(thumbnail_url: str) -> Optional[bytes]:
    """Download cover image from URL; return bytes or None. Prefer higher-res SoundCloud art."""
    if not thumbnail_url or not thumbnail_url.strip():
        return None
    url = thumbnail_url.strip()
    # SoundCloud: prefer larger art (t500x500 or t300x300)
    if "soundcloud" in url and "-large" in url:
        url = url.replace("-large", "-t500x500")
    try:
        req = Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"},
        )
        with urlopen(req, timeout=15) as r:
            return r.read()
    except Exception:
        return None


def _download_soundcloud_playlist(url: str, quality: str, audio_format: str = "mp3") -> tuple[bytes, str]:
    """Download full SoundCloud playlist to a zip (tracks + cover + playlist info). Returns (zip_bytes, suggested_filename)."""
    folder = Path(app.config["DOWNLOAD_FOLDER"])
    run_id = str(uuid.uuid4())[:8]
    playlist_dir = folder / f"sc_pl_{run_id}"
    playlist_dir.mkdir(exist_ok=True)

    out_tmpl = str(playlist_dir / "%(playlist_index)03d - %(title)s.%(ext)s")
    opts = get_ydl_opts_soundcloud(out_tmpl, quality, audio_format)
    opts["noplaylist"] = False
    opts["sleep_requests"] = 0.5  # reduce rate-limit risk on SoundCloud

    try:
        with YoutubeDL(opts) as ydl:
            # Get playlist metadata first (no download)
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not get playlist info")
            pl_title = info.get("title") or "Playlist"
            pl_desc = info.get("description") or ""
            entries = info.get("entries") or []
            track_titles = []
            for e in entries:
                if e and e.get("title"):
                    track_titles.append(e["title"])

            # Resolve playlist cover URL (playlist thumbnail, or first track's art)
            thumbnail_url = info.get("thumbnail") or ""
            if not thumbnail_url and info.get("thumbnails"):
                thumbs = info.get("thumbnails") or []
                if thumbs:
                    thumbnail_url = thumbs[-1].get("url") if isinstance(thumbs[-1], dict) else ""
            if not thumbnail_url and entries:
                first = entries[0]
                if isinstance(first, dict):
                    thumbnail_url = first.get("thumbnail") or ""
                    if not thumbnail_url and first.get("thumbnails"):
                        t = first["thumbnails"][-1]
                        thumbnail_url = t.get("url", "") if isinstance(t, dict) else ""

            # Download all tracks
            ydl.download([url])

            # Download playlist cover image and save as cover.jpg in the folder (included in zip)
            cover_data = _fetch_cover_image(thumbnail_url)
            if not cover_data and entries:
                first = entries[0]
                if isinstance(first, dict):
                    fallback_url = first.get("thumbnail") or ""
                    if not fallback_url and first.get("thumbnails"):
                        t = first["thumbnails"][-1]
                        fallback_url = t.get("url", "") if isinstance(t, dict) else ""
                    cover_data = _fetch_cover_image(fallback_url)
            if cover_data:
                ext = "jpg" if cover_data[:3] == b"\xff\xd8\xff" else "png" if cover_data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
                (playlist_dir / f"cover.{ext}").write_bytes(cover_data)

            # Playlist info file
            lines = [
                pl_title,
                "",
                pl_desc,
                "",
                "--- Tracks ---",
                *[f"{i+1}. {t}" for i, t in enumerate(track_titles)],
            ]
            (playlist_dir / "playlist.txt").write_text("\n".join(lines), encoding="utf-8")

            safe_pl_name = _sanitize_filename(pl_title, 80)
            zip_name = f"{safe_pl_name}.zip"

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add cover first if present, then playlist.txt, then tracks
                for f in sorted(playlist_dir.iterdir(), key=lambda x: (0 if x.name.startswith("cover.") else 1 if x.name == "playlist.txt" else 2, x.name)):
                    zf.write(f, f.name)

            return buf.getvalue(), zip_name
    finally:
        try:
            for f in playlist_dir.iterdir():
                f.unlink()
            playlist_dir.rmdir()
        except OSError:
            pass


@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    source = (data.get("source") or "youtube").lower()
    as_playlist = data.get("playlist") is True
    fmt = (data.get("format") or "mp4").lower()
    quality = (data.get("quality") or "best").lower()

    if not url:
        return jsonify({"ok": False, "error": "No URL provided"}), 400

    # --- SoundCloud: single track or playlist ---
    if source == "soundcloud":
        if not is_soundcloud_url(url):
            return jsonify({"ok": False, "error": "Invalid SoundCloud URL"}), 400
        audio_fmt = fmt if fmt in ("mp3", "wav") else "mp3"
        if quality not in (*MP3_QUALITY_BITRATE, "best"):
            quality = "best"

        if as_playlist and is_soundcloud_playlist(url):
            try:
                zip_bytes, zip_name = _download_soundcloud_playlist(url, quality, audio_fmt)
                return send_file(
                    io.BytesIO(zip_bytes),
                    as_attachment=True,
                    download_name=zip_name,
                    mimetype="application/zip",
                )
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)}), 400
        else:
            # Single SoundCloud track
            file_id = str(uuid.uuid4())[:8]
            base_name = f"sc_{file_id}"
            folder = app.config["DOWNLOAD_FOLDER"]
            out_template = os.path.join(folder, f"{base_name}.%(ext)s")
            opts = get_ydl_opts_soundcloud(out_template, quality, audio_fmt)
            opts["noplaylist"] = True
            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return jsonify({"ok": False, "error": "Could not get track info"}), 400
                    title = info.get("title") or base_name
                    safe_title = _sanitize_filename(title, 80)
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)}), 400
            candidates = list(Path(folder).glob(f"{base_name}*"))
            if not candidates:
                return jsonify({"ok": False, "error": "Download failed"}), 500
            out_file = candidates[0]
            mime = "audio/wav" if audio_fmt == "wav" else "audio/mpeg"
            try:
                return send_file(
                    str(out_file),
                    as_attachment=True,
                    download_name=f"{safe_title}.{audio_fmt}",
                    mimetype=mime,
                )
            finally:
                try:
                    out_file.unlink()
                except OSError:
                    pass
    # --- YouTube ---
    if not is_youtube_url(url):
        return jsonify({"ok": False, "error": "Invalid YouTube URL"}), 400
    if fmt not in ("mp3", "mp4", "wav"):
        return jsonify({"ok": False, "error": "Format must be mp4, mp3, or wav"}), 400

    file_id = str(uuid.uuid4())[:8]
    base_name = f"yt_{file_id}"
    folder = app.config["DOWNLOAD_FOLDER"]

    if fmt == "mp4":
        out_template = os.path.join(folder, f"{base_name}.%(ext)s")
        opts = get_ydl_opts_mp4(out_template, quality)
    else:
        out_template = os.path.join(folder, f"{base_name}.%(ext)s")
        opts = get_ydl_opts_audio(out_template, fmt, quality)

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return jsonify({"ok": False, "error": "Could not get video info"}), 400
            title = info.get("title") or base_name
            safe_title = _sanitize_filename(title, 80)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    candidates = list(Path(folder).glob(f"{base_name}*"))
    if not candidates:
        return jsonify({"ok": False, "error": "Download failed"}), 500

    out_file = candidates[0]
    mime = "video/mp4" if fmt == "mp4" else ("audio/wav" if fmt == "wav" else "audio/mpeg")
    try:
        return send_file(
            str(out_file),
            as_attachment=True,
            download_name=f"{safe_title}.{fmt}",
            mimetype=mime,
        )
    finally:
        try:
            out_file.unlink()
        except OSError:
            pass


@app.route("/api/validate", methods=["POST"])
def validate():
    """Validate URL and return detected source (youtube/soundcloud) and whether it's a playlist."""
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"ok": False, "valid": False})
    if is_youtube_url(url):
        return jsonify({"ok": True, "valid": True, "source": "youtube", "playlist": False})
    if is_soundcloud_url(url):
        return jsonify({
            "ok": True,
            "valid": True,
            "source": "soundcloud",
            "playlist": is_soundcloud_playlist(url),
        })
    return jsonify({"ok": True, "valid": False})


def main():
    port = 5000
    url = f"http://127.0.0.1:{port}"

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    if getattr(sys, "frozen", False):
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        print("YouTube & SoundCloud Downloader")
        print(f"Opening {url} in your browser. Close this window to stop the app.\n")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
