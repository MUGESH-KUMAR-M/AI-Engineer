#!/usr/bin/env pwsh
# RAG Chatbot Complete Startup Script
# Runs both backend and frontend servers

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 SWS AI RAG Chatbot - Complete Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

try {
    Write-Info "Step 1: Checking Python environment..."
    if (!(Test-Path ".\venv\Scripts\python.exe")) {
        Write-Warning "Virtual environment not found. Creating..."
        python -m venv venv
    }
    Write-Success "✓ Virtual environment ready"
    Write-Host ""

    Write-Info "Step 2: Activating virtual environment..."
    & .\venv\Scripts\Activate.ps1
    Write-Success "✓ Virtual environment activated"
    Write-Host ""

    Write-Info "Step 3: Installing dependencies..."
    pip install -q -r requirements.txt
    Write-Success "✓ Dependencies installed"
    Write-Host ""

    Write-Info "Step 4: Checking vector database..."
    if (!(Test-Path "data\chroma_db")) {
        Write-Warning "Vector database not found. Running ingestion..."
        python -m backend.ingest
        Write-Success "✓ Documents ingested"
    } else {
        Write-Success "✓ Vector database found"
    }
    Write-Host ""

    Write-Info "Starting servers..."
    Write-Host ""
    Write-Host "Backend Server: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "Frontend Server: http://localhost:5173" -ForegroundColor Yellow
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Warning "Press Ctrl+C to stop servers"
    Write-Host ""

    # Start backend
    Write-Host "Starting backend..." -ForegroundColor Magenta
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
