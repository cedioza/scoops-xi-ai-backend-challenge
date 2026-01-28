# PowerShell script to setup local environment
Write-Host "Setting up local environment for Scoops XI AI Backend..." -ForegroundColor Cyan

# Create venv
if (-not (Test-Path -Path ".venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}

# Activate and install
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& .\.venv\Scripts\pip install -r requirements.txt

Write-Host "`nSetup complete! To activate the environment, run:" -ForegroundColor Green
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor White
