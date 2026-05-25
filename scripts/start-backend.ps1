$ErrorActionPreference = "Stop"

$backendPath = Join-Path $PSScriptRoot "..\backend"
Set-Location $backendPath

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
    pip install -r requirements-dev.txt
}

alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
