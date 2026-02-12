@echo off
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
echo Building executable...
python -m PyInstaller --noconfirm downloader.spec
if %ERRORLEVEL% EQU 0 (
    echo Done. Run: dist\YouTube Downloader.exe
) else (
    echo Build failed.
)
pause
