$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Project virtual environment not found at .venv. Create it and install the packages listed in requirements.txt\requirement."
}

Write-Host 'Starting ComicCraft at http://127.0.0.1:8000'
Write-Host 'Press Ctrl+C to stop the server.'
& $Python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
