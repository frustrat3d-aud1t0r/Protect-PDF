<#
.SYNOPSIS
    PDF Password Protection Tool - Python Wrapper

.DESCRIPTION
    Simple PowerShell wrapper for the Python protect_pdf.py script
    This gives you drag-and-drop functionality while using the stable Python backend

    Version: 1.0.5
    Developed by: Kenny Robertson Tan
    Output Location: OUTPUT folder (auto-created)

.PARAMETER InputPDF
    Path to the unprotected PDF file

.EXAMPLE
    .\Protect-PDF-Simple.ps1 -InputPDF "document.pdf"

.EXAMPLE
    Drag and drop a PDF file onto Protect-PDF-Simple.bat

.NOTES
    CHANGELOG:

    v1.0.5 (2025-10-25):
        - Suppressed library check messages when already installed
        - Cleaner terminal output - only shows messages when action needed
        - Removed redundant success message at the end

    v1.0.4 (2025-10-24):
        - Removed backup functionality for cleaner workflow
        - Output files now saved to OUTPUT folder
        - Scripts moved to scripts/ subfolder for organization
        - Fixed terminal box alignment issues
        - Added beautiful colored terminal output with emojis and icons
        - Added ASCII banner display
        - Changed timestamp format from HHMM to YYYYMMDD
        - Auto-creates OUTPUT folder for encrypted PDFs
        - Added terminal window title
        - Owner password requires minimum 12 characters
        - Owner password must be different from user password
        - Owner password now allows copy and modify permissions
        - Added high-quality printing permission for all users
        - Removed password confirmation for faster workflow

    v1.0.3 (2025-10-24):
        - Improved terminal UI with colors and borders
        - Enhanced status messages with icons

    v1.0.2 (2025-10-24):
        - Initial version with automatic Python installation
        - Auto-install PyMuPDF library
        - AES-256 encryption support
        - Password strength validation
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$InputPDF
)

$ScriptVersion = "1.0.5"

# Check if Python is installed (silent check)
$pythonCommand = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $cmd
            break
        }
    }
    catch {
        continue
    }
}

if (-not $pythonCommand) {
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "PDF PASSWORD PROTECTION TOOL (PowerShell + Python)" -ForegroundColor Cyan
    Write-Host "Version: $ScriptVersion" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[WARNING] Python is not installed or not in PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[INFO] Attempting automatic installation using Windows Package Manager (winget)..." -ForegroundColor Cyan

    # Check if winget is available
    $wingetAvailable = $false
    try {
        $wingetVersion = & winget --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $wingetAvailable = $true
            Write-Host "[SUCCESS] winget is available: $wingetVersion" -ForegroundColor Green
        }
    }
    catch {
        $wingetAvailable = $false
    }

    if ($wingetAvailable) {
        Write-Host "[INFO] Installing Python 3.12 via winget (this may take a few minutes)..." -ForegroundColor Cyan
        Write-Host "[INFO] You may see a prompt - please accept to continue installation" -ForegroundColor Yellow

        # Install Python using winget
        & winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Python installed successfully!" -ForegroundColor Green
            Write-Host "[INFO] Refreshing environment variables..." -ForegroundColor Cyan

            # Refresh PATH environment variable
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

            # Try to find Python again
            Start-Sleep -Seconds 2
            foreach ($cmd in @("python", "python3", "py")) {
                try {
                    $version = & $cmd --version 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        $pythonCommand = $cmd
                        Write-Host "[SUCCESS] Python is now available: $version" -ForegroundColor Green
                        break
                    }
                }
                catch {
                    continue
                }
            }

            if (-not $pythonCommand) {
                Write-Host "[WARNING] Python was installed but requires restart" -ForegroundColor Yellow
                Write-Host "[ACTION] Please close this window and run the script again" -ForegroundColor Cyan
                exit 1
            }
        }
        else {
            Write-Host "[ERROR] Automatic installation failed" -ForegroundColor Red
            Write-Host ""
            Write-Host "[MANUAL INSTALLATION REQUIRED]" -ForegroundColor Yellow
            Write-Host "Please install Python manually:" -ForegroundColor White
            Write-Host "1. Visit: https://www.python.org/downloads/" -ForegroundColor White
            Write-Host "2. Download and run the installer" -ForegroundColor White
            Write-Host "3. IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor White
            Write-Host "4. Run this script again after installation" -ForegroundColor White
            exit 1
        }
    }
    else {
        Write-Host "[WARNING] Windows Package Manager (winget) is not available" -ForegroundColor Yellow
        Write-Host "[INFO] winget requires Windows 10 version 1809 or later" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "[MANUAL INSTALLATION REQUIRED]" -ForegroundColor Yellow
        Write-Host "Please install Python manually:" -ForegroundColor White
        Write-Host "1. Visit: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Download and run the installer" -ForegroundColor White
        Write-Host "3. IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor White
        Write-Host "4. Run this script again after installation" -ForegroundColor White
        exit 1
    }
}

# Check if PyMuPDF (fitz) is installed (silent check)
$checkFitz = & $pythonCommand -c "import fitz; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "PDF PASSWORD PROTECTION TOOL (PowerShell + Python)" -ForegroundColor Cyan
    Write-Host "Version: $ScriptVersion" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[WARNING] PyMuPDF is not installed. Installing now..." -ForegroundColor Yellow
    Write-Host "[INFO] Running: pip install PyMuPDF" -ForegroundColor Cyan

    & $pythonCommand -m pip install PyMuPDF

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install PyMuPDF" -ForegroundColor Red
        Write-Host "Please run manually: pip install PyMuPDF" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[SUCCESS] PyMuPDF installed successfully" -ForegroundColor Green
    Write-Host ""
}

# Locate the Python script
$pythonScript = Join-Path $PSScriptRoot "protect_pdf.py"

if (-not (Test-Path $pythonScript)) {
    Write-Host "[ERROR] protect_pdf.py not found in: $PSScriptRoot" -ForegroundColor Red
    exit 1
}

# Run the Python script
if ([string]::IsNullOrEmpty($InputPDF)) {
    # No argument - let Python script prompt for input
    & $pythonCommand $pythonScript
} else {
    # PDF file provided as argument
    & $pythonCommand $pythonScript $InputPDF
}

# Check exit code and only show if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Operation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}

exit $LASTEXITCODE
