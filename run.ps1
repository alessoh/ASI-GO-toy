# PowerShell start script for Toy ASI-ARCH

Write-Host "Starting Toy ASI-ARCH..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv"
    Write-Host "Then run: pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the main program
python main.py

# Check if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "An error occurred. Check the logs for details." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}