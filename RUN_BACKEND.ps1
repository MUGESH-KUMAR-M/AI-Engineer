# Restart SWS AI backend on port 8010 (kills stale process first)
$port = 8010
$conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $conns) {
    if ($pid -gt 0) {
        Write-Host "Stopping process on port $port (PID $pid)..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2
Set-Location $PSScriptRoot
Write-Host "Starting backend on http://127.0.0.1:$port ..."
& .\venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port $port --reload
