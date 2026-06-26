Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  URL Shortener with ngrok - Mobile QR Code Setup          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking for ngrok..." -ForegroundColor Yellow
try {
    $ngrokPath = Get-Command ngrok -ErrorAction Stop
    Write-Host "✓ ngrok found at: $($ngrokPath.Source)" -ForegroundColor Green
} catch {
    Write-Host "✗ ngrok not found! Please install ngrok from https://ngrok.com/download" -ForegroundColor Red
    Write-Host ""
    Write-Host "After installing, add it to PATH or run from ngrok directory." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""
Write-Host "Starting ngrok tunnel (port 8000)..." -ForegroundColor Yellow
Start-Process ngrok -ArgumentList "http 8000" -NoNewWindow -PassThru | Out-Null
Write-Host "✓ ngrok tunnel starting..." -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Waiting for ngrok to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Retrieving public ngrok URL..." -ForegroundColor Yellow
try {
    $ngrokResponse = Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" -UseBasicParsing | ConvertFrom-Json
    $ngrokUrl = $ngrokResponse.tunnels[0].public_url
    
    if ($ngrokUrl) {
        Write-Host "✓ ngrok public URL: $ngrokUrl" -ForegroundColor Green
        Write-Host ""
        Write-Host "Setting NGROK_URL environment variable..." -ForegroundColor Yellow
        $env:NGROK_URL = $ngrokUrl
        Write-Host "✓ NGROK_URL=$ngrokUrl" -ForegroundColor Green
    } else {
        Write-Host "✗ Could not retrieve ngrok URL" -ForegroundColor Red
        Write-Host "Please check ngrok tunnel at http://localhost:4040" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not retrieve ngrok URL automatically" -ForegroundColor Yellow
    Write-Host "Manually set NGROK_URL from: http://localhost:4040" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Once you have the URL, you can set it manually:" -ForegroundColor Yellow
    Write-Host "`$env:NGROK_URL='https://your-ngrok-url.ngrok.io'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Starting FastAPI application (port 8000)..." -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Application stopped. ngrok tunnel is still running." -ForegroundColor Yellow
Write-Host "Access ngrok dashboard: http://localhost:4040" -ForegroundColor Cyan
Write-Host ""
