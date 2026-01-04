# Discord Cat Bot - Windows Service Installer using NSSM
# Run this script as Administrator

Write-Host "Discord Cat Bot - Windows Service Installer" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

$botDir = $PSScriptRoot
Write-Host "Bot directory: $botDir" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path "$botDir\.env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your DISCORD_BOT_TOKEN" -ForegroundColor Yellow
    pause
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "$botDir\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "$botDir\venv\Scripts\Activate.ps1"
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    deactivate
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Check if NSSM is available
$nssmPath = "nssm.exe"
if (-not (Get-Command $nssmPath -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "NSSM (Non-Sucking Service Manager) not found!" -ForegroundColor Yellow
    Write-Host "Download it from: https://nssm.cc/download" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or install via Chocolatey: choco install nssm" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternative: Use the run-windows-service.bat file instead" -ForegroundColor Yellow
    pause
    exit 1
}

$serviceName = "DiscordCatBot"
$pythonExe = "$botDir\venv\Scripts\python.exe"
$botScript = "$botDir\bot.py"

# Remove existing service if it exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Removing existing service..." -ForegroundColor Yellow
    nssm stop $serviceName
    nssm remove $serviceName confirm
}

# Install the service
Write-Host "Installing service..." -ForegroundColor Yellow
nssm install $serviceName $pythonExe $botScript
nssm set $serviceName AppDirectory $botDir
nssm set $serviceName DisplayName "Discord Cat Bot"
nssm set $serviceName Description "A Discord bot that sends cat pictures from cataas.com"
nssm set $serviceName Start SERVICE_AUTO_START
nssm set $serviceName AppExit Default Restart
nssm set $serviceName AppRestartDelay 10000

# Start the service
Write-Host "Starting service..." -ForegroundColor Yellow
nssm start $serviceName

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  nssm status $serviceName      # Check bot status"
Write-Host "  nssm stop $serviceName        # Stop the bot"
Write-Host "  nssm start $serviceName       # Start the bot"
Write-Host "  nssm restart $serviceName     # Restart the bot"
Write-Host "  nssm remove $serviceName      # Uninstall the service"
Write-Host ""
Write-Host "Or use Windows Services (services.msc) to manage the bot" -ForegroundColor Yellow
Write-Host ""
pause

