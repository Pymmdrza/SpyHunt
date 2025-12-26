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
    $fc = $host.UI.RawUI. ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
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
                    Version: 4.0.3
            https://github.com/Pymmdrza/SpyHunt

"@ -ForegroundColor Cyan
}

# Check Python
function Test-Python {
    Write-Info "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\. ([7-9]|1[0-9])") {
            Write-Success "Python found:  $pythonVersion"
            return $true
        }
    } catch {}
    
    try {
        $python3Version = python3 --version 2>&1
        if ($python3Version -match "Python 3\.([7-9]|1[0-9])") {
            Write-Success "Python3 found: $python3Version"
            return $true
        }
    } catch {}
    
    return $false
}

# Install Python
function Install-Python {
    Write-Info "Installing Python..."
    
    # Check for winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Python. Python.3.11 --silent
    }
    # Check for chocolatey
    elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install python3 -y
    }
    else {
        Write-Error "Please install Python 3.7+ manually from https://python.org"
        exit 1
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]:: GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Success "Python installed successfully"
}

# Install SpyHunt
function Install-SpyHunt {
    Write-Info "Installing SpyHunt..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install SpyHunt
    python -m pip install spyhunt
    
    Write-Success "SpyHunt installed successfully"
}

# Install from source
function Install-FromSource {
    Write-Info "Installing SpyHunt from source..."
    
    $installDir = "$env: USERPROFILE\. spyhunt"
    
    # Create directory
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # Clone repository
    if (Test-Path "$installDir\SpyHunt") {
        Write-Info "Updating existing installation..."
        Set-Location "$installDir\SpyHunt"
        git pull origin main
    } else {
        Set-Location $installDir
        git clone --depth 1 https://github.com/Pymmdrza/SpyHunt.git
    }
    
    # Install
    Set-Location "$installDir\SpyHunt"
    python -m pip install -e .
    
    Write-Success "SpyHunt installed from source"
}

# Uninstall
function Uninstall-SpyHunt {
    Write-Info "Uninstalling SpyHunt..."
    
    python -m pip uninstall spyhunt -y
    
    $installDir = "$env: USERPROFILE\. spyhunt"
    if (Test-Path $installDir) {
        Remove-Item -Recurse -Force $installDir
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
  irm https://raw.githubusercontent.com/Pymmdrza/SpyHunt/main/install. ps1 | iex
  .\install.ps1 -Pip
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
        Install-Python
    }
    
    # Install
    if ($Pip) {
        Install-SpyHunt
    } else {
        Install-SpyHunt
    }
    
    # Verify
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              Installation Complete!                            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  spyhunt --help              Show help message" -ForegroundColor Cyan
    Write-Host "  spyhunt -u example. com      Scan a target" -ForegroundColor Cyan
    Write-Host ""
}

Main
