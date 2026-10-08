@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Project virtual environment not found at .venv.
    echo Install dependencies from requirements.txt\requirement first.
    exit /b 1
)
echo Starting ComicCraft at http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
