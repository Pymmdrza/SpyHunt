# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                    SpyHunt v4.0 - Windows Installer                        ║
# ║        A comprehensive Network Scanner & Vulnerability Assessment tool     ║
# ║                      https://github.com/Pymmdrza/SpyHunt                   ║
# ╚════════════════════════════════════════════════════════════════════════════╝

param(
    [switch]$Pip,
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI. ForegroundColor = $fc
}

function Write-Info($message) {
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $message
}

function Write-Success($message) {
    Write-Host "[✓] " -ForegroundColor Green -NoNewline
    Write-Host $message
}

function Write-Warning($message) {
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $message
}

function Write-Error($message) {
    Write-Host "[✗] " -ForegroundColor Red -NoNewline
    Write-Host $message
}

# Banner
function Show-Banner {
    Write-Host @"

   _____ _____  __     __ _    _ _    _ _   _ _______ 
  / ____|  __ \ \ \   / /| |  | | |  | | \ | |__   __|
 | (___ | |__) | \ \_/ / | |__| | |  | |  \| |  | |   
  \___ \|  ___/   \   /  |  __  | |  | | . ` |  | |   
  ____) | |        | |   | |  | | |__| | |\  |  | |   
 |_____/|_|        |_|   |_|  |_|\____/|_| \_|  |_|   
                                                       
        Network Scanner & Vulnerability Assessment Tool
                    Version:  4.0.3
            https://github.com/Pymmdrza/SpyHunt

"@ -ForegroundColor Cyan
}

# Check Python
function Test-Python {
    Write-Info "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\. ([7-9]|1[0-9])") {
            Write-Success "Python found: $pythonVersion"
            return $true
        }
    } catch {
        Write-Warning "Python command not found"
    }
    
    try {
        $python3Version = python3 --version 2>&1
        if ($python3Version -match "Python 3\. ([7-9]|1[0-9])") {
            Write-Success "Python3 found: $python3Version"
            return $true
        }
    } catch {
        Write-Warning "Python3 command not found"
    }
    
    return $false
}

# Install Python
function Install-Python {
    Write-Info "Installing Python..."
    
    # Check for winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        try {
            winget install Python. Python.3.11 --silent --accept-source-agreements --accept-package-agreements
            Write-Success "Python installed via winget"
        } catch {
            Write-Error "Failed to install Python via winget:  $_"
            exit 1
        }
    }
    # Check for chocolatey
    elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        try {
            choco install python3 -y
            Write-Success "Python installed via chocolatey"
        } catch {
            Write-Error "Failed to install Python via chocolatey: $_"
            exit 1
        }
    }
    else {
        Write-Error "No package manager found.  Please install Python 3.7+ manually from https://python.org"
        Write-Info "Or install winget/chocolatey first"
        exit 1
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]:: GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Wait for PATH to update
    Start-Sleep -Seconds 2
    
    # Verify installation
    if (-not (Test-Python)) {
        Write-Warning "Python installed but not found in PATH.  Please restart PowerShell and run the installer again."
        exit 1
    }
}

# Install SpyHunt
function Install-SpyHunt {
    Write-Info "Installing SpyHunt..."
    
    try {
        # Upgrade pip
        Write-Info "Upgrading pip..."
        python -m pip install --upgrade pip --quiet
        
        # Install SpyHunt
        Write-Info "Installing SpyHunt package..."
        python -m pip install spyhunt --upgrade
        
        Write-Success "SpyHunt installed successfully"
    } catch {
        Write-Error "Failed to install SpyHunt: $_"
        Write-Info "Trying alternative installation method..."
        Install-FromSource
    }
}

# Install from source
function Install-FromSource {
    Write-Info "Installing SpyHunt from source..."
    
    # Check for git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git is not installed. Please install Git first or use:  .\install.ps1 -Pip"
        exit 1
    }
    
    $installDir = "$env: USERPROFILE\.spyhunt"
    
    try {
        # Create directory
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        }
        
        # Clone or update repository
        if (Test-Path "$installDir\SpyHunt") {
            Write-Info "Updating existing installation..."
            Set-Location "$installDir\SpyHunt"
            git pull origin main
        } else {
            Write-Info "Cloning repository..."
            Set-Location $installDir
            git clone --depth 1 https://github.com/Pymmdrza/SpyHunt.git
        }
        
        # Install
        Set-Location "$installDir\SpyHunt"
        python -m pip install -e .
        
        Write-Success "SpyHunt installed from source"
    } catch {
        Write-Error "Failed to install from source: $_"
        exit 1
    }
}

# Uninstall
function Uninstall-SpyHunt {
    Write-Info "Uninstalling SpyHunt..."
    
    try {
        python -m pip uninstall spyhunt -y 2>$null
    } catch {
        Write-Warning "SpyHunt package not found in pip"
    }
    
    $installDir = "$env:USERPROFILE\.spyhunt"
    if (Test-Path $installDir) {
        try {
            Remove-Item -Recurse -Force $installDir
            Write-Success "Removed installation directory"
        } catch {
            Write-Warning "Could not remove installation directory: $_"
        }
    }
    
    Write-Success "SpyHunt uninstalled successfully"
}

# Show help
function Show-Help {
    Show-Banner
    Write-Host @"
Usage: .\install.ps1 [OPTIONS]

Options:
  -Pip          Install via pip (default)
  -Uninstall    Remove SpyHunt
  -Help         Show this help message

Examples:
  irm https://raw.githubusercontent.com/Pymmdrza/SpyHunt/main/install.ps1 | iex
  .\install. ps1 -Pip
  .\install.ps1 -Uninstall

"@
}

# Main
function Main {
    Show-Banner
    
    if ($Help) {
        Show-Help
        return
    }
    
    if ($Uninstall) {
        Uninstall-SpyHunt
        return
    }
    
    # Check Python
    if (-not (Test-Python)) {
        Write-Warning "Python 3.7+ is required but not found"
        $install = Read-Host "Would you like to install Python now? (Y/N)"
        if ($install -eq 'Y' -or $install -eq 'y') {
            Install-Python
        } else {
            Write-Error "Installation cancelled.  Please install Python manually and try again."
            exit 1
        }
    }
    
    # Install
    if ($Pip) {
        Install-SpyHunt
    } else {
        Install-SpyHunt
    }
    
    # Verify installation
    try {
        $verifyOutput = python -m pip show spyhunt 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
            Write-Host "║              Installation Complete!                            ║" -ForegroundColor Green
            Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor White
            Write-Host "  spyhunt --help              Show help message" -ForegroundColor Cyan
            Write-Host "  spyhunt -u example.com      Scan a target" -ForegroundColor Cyan
            Write-Host ""
        } else {
            Write-Warning "Installation completed but verification failed"
        }
    } catch {
        Write-Warning "Could not verify installation"
    }
}

# Run main function
try {
    Main
} catch {
    Write-Error "An unexpected error occurred:  $_"
    exit 1
}
