@echo off
setlocal
REM Builds a GitHub-release-ready folder: exe + bundled FFmpeg.
REM Run from project root. Requires: Python, pip install -r requirements.txt pyinstaller
REM Output: release\YouTube Downloader\ (zip this and upload to GitHub Releases)

cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

set "RELEASE_DIR=release\YouTube Downloader"
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "FFMPEG_ZIP=release\ffmpeg.zip"

echo [1/4] Building executable...
python -m PyInstaller --noconfirm downloader.spec
if %ERRORLEVEL% NEQ 0 goto :fail

echo [2/4] Creating release folder...
if exist "release" rmdir /s /q "release"
mkdir "%RELEASE_DIR%"
copy "dist\YouTube Downloader.exe" "%RELEASE_DIR%\YouTube Downloader.exe"

echo [3/4] Downloading FFmpeg (this may take a minute)...
powershell -NoProfile -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%' -UseBasicParsing }"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to download FFmpeg. Create "%RELEASE_DIR%\ffmpeg" and add ffmpeg.exe and ffprobe.exe manually, then zip "%RELEASE_DIR%"
    goto :fail
)

echo [4/4] Extracting FFmpeg into release folder...
mkdir "%RELEASE_DIR%\ffmpeg"
powershell -NoProfile -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath 'release' -Force"
for /d %%d in (release\ffmpeg-*) do (
    copy "%%d\bin\ffmpeg.exe" "%RELEASE_DIR%\ffmpeg\"
    copy "%%d\bin\ffprobe.exe" "%RELEASE_DIR%\ffmpeg\"
    rmdir /s /q "%%d"
    goto :done_ffmpeg
)
:done_ffmpeg
del "%FFMPEG_ZIP%" 2>nul

echo.
echo Done. Release folder: %RELEASE_DIR%
echo   - YouTube Downloader.exe
echo   - ffmpeg\ffmpeg.exe, ffprobe.exe
echo.
echo Zip the folder "%RELEASE_DIR%" and upload to GitHub Releases so users can download and run the exe with no setup.
goto :end
:fail
echo.
echo Build failed. Check the messages above.
:end
pause
