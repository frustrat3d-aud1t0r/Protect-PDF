@echo off
REM =========================================================================
REM PDF Password Protection Tool - Simple Python Wrapper
REM Version: 1.0.5
REM Developed by: Kenny Robertson Tan
REM =========================================================================
REM Works directly on Windows without complex .NET dependencies
REM Output files saved to OUTPUT folder
REM
REM CHANGELOG:
REM   v1.0.5 (2025-10-25):
REM     - Suppressed library check messages when already installed
REM     - Cleaner terminal output - only shows messages when action needed
REM     - Removed redundant success message at the end
REM
REM   v1.0.4 (2025-10-24):
REM     - Removed backup functionality for cleaner workflow
REM     - Output files now saved to OUTPUT folder
REM     - Scripts moved to scripts/ subfolder
REM     - Fixed terminal box alignment
REM     - Added colored terminal output with emojis
REM     - Added ASCII banner display
REM     - Changed timestamp format HHMM to YYYYMMDD
REM     - Added terminal window title
REM     - Owner password requires minimum 12 characters
REM     - Owner password must be different from user password
REM     - Owner password now allows copy and modify permissions
REM     - Added high-quality printing permission for all users
REM     - Removed password confirmation for faster workflow
REM
REM   v1.0.3 (2025-10-24):
REM     - Added developer credit
REM     - Improved terminal UI with colors
REM
REM   v1.0.2 (2025-10-24):
REM     - Initial version with auto Python installation
REM =========================================================================

REM Set terminal window title
title PDF Password Protection Tool v1.0.5 - by Kenny Robertson Tan

setlocal

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Check if a PDF file was dragged onto the batch file
if "%~1"=="" (
    REM No file provided - run in interactive mode
    PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\Protect-PDF-Simple.ps1"
) else (
    REM File was dragged - pass it as parameter
    PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\Protect-PDF-Simple.ps1" -InputPDF "%~1"
)

REM Keep window open to see results
echo.
echo Press any key to close this window...
pause >nul
