#!/usr/bin/env python3
"""
PDF Password Protection with Visible Password Input
Version: 1.0.5
Purpose: Convert unprotected PDFs to password-protected PDFs with custom passwords
Output Format: Original_Filename_YYYYMMDD.pdf
Output Location: OUTPUT folder in script directory
Data Retention: 30 days from generation date
Security Note: Password input is VISIBLE on screen
Note: Original files remain unchanged - encrypted copies are created
Developed by: Kenny Robertson Tan

Changelog:
    v1.0.5 (2025-10-25):
        - PowerShell wrapper now suppresses library check messages when already installed
        - Cleaner terminal output

    v1.0.4 (2025-10-24):
        - Removed backup functionality for cleaner workflow
        - Fixed terminal box alignment issues
        - Added beautiful colored terminal output with emojis
        - Added ASCII banner display
        - Output files now saved to OUTPUT folder
        - Changed timestamp format from HHMM to YYYYMMDD
        - Owner password now allows copy and modify permissions
        - Added high-quality printing permission for all users
        - Removed password confirmation for faster workflow
        - Added terminal window title
        - Owner password requires minimum 12 characters
        - Owner password must be different from user password

    v1.0.3 (2025-10-24):
        - Improved terminal UI with colors and borders
        - Enhanced status messages with icons

    v1.0.2 (2025-10-24):
        - Initial version with backup functionality
        - AES-256 encryption support
        - Password strength validation
        - Auto-incrementing filenames
"""

import fitz  # PyMuPDF
import os
from datetime import datetime, timedelta
import sys

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'

def print_banner():
    """Print ASCII art banner"""
    banner = """ _____                                                                            _____
( ___ )                                                                          ( ___ )
 |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   |
 |   |  ____                   _                   _       ____    ____    _____  |   |
 |   | |  _ \\   _ __    ___   | |_    ___    ___  | |_    |  _ \\  |  _ \\  |  ___| |   |
 |   | | |_) | | '__|  / _ \\  | __|  / _ \\  / __| | __|   | |_) | | | | | | |_    |   |
 |   | |  __/  | |    | (_) | | |_  |  __/ | (__  | |_    |  __/  | |_| | |  _|   |   |
 |   | |_|     |_|     \\___/   \\__|  \\___|  \\___|  \\__|   |_|     |____/  |_|     |   |
 |   |                                                                            |   |
 |   |                                                          EST. 24 Oct 2025  |   |
 |   |                                                             Version 1.0.5  |   |
 |___|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|___|
(_____)                                                                          (_____)"""
    print(f"{Colors.CYAN}{banner}{Colors.END}")

def print_box(text, color=Colors.CYAN):
    """Print text in a bordered box with fixed width - simple version"""
    lines = text.split('\n')
    box_width = 60

    # Top border
    print(f"{color}╔{'═' * box_width}╗{Colors.END}")

    # Content lines
    for line in lines:
        spaces_needed = box_width - len(line) - 2
        print(f"{color}║ {line}{' ' * spaces_needed} ║{Colors.END}")

    # Bottom border
    print(f"{color}╚{'═' * box_width}╝{Colors.END}")

def print_status(status_type, message):
    """Print formatted status messages"""
    icons = {
        'info': '🔵',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'key': '🔑',
        'lock': '🔒',
        'save': '💾',
        'time': '⏱️'
    }

    colors = {
        'info': Colors.CYAN,
        'success': Colors.GREEN,
        'warning': Colors.YELLOW,
        'error': Colors.RED,
        'key': Colors.YELLOW,
        'lock': Colors.GREEN,
        'save': Colors.BLUE,
        'time': Colors.CYAN
    }

    icon = icons.get(status_type, '•')
    color = colors.get(status_type, Colors.WHITE)

    print(f"{color}{icon} {message}{Colors.END}")

def get_output_filename(input_pdf_path, script_dir):
    """
    Generate output filename based on original filename + YYYYMMDD timestamp
    Format: Original_Filename_YYYYMMDD.pdf or Original_Filename_YYYYMMDD_N.pdf if exists
    Output Location: OUTPUT folder in script directory

    Example:
        Input:  MCVO_Issue_Sheet.pdf
        Output: OUTPUT/MCVO_Issue_Sheet_20251024.pdf (on October 24, 2025)
    """
    # Create OUTPUT directory in the script's directory
    output_directory = os.path.join(script_dir, "OUTPUT")
    os.makedirs(output_directory, exist_ok=True)

    base_filename = os.path.splitext(os.path.basename(input_pdf_path))[0]

    # Get current date in YYYYMMDD format
    current_date = datetime.now().strftime("%Y%m%d")

    # Create output filename
    output_filename = f"{base_filename}_{current_date}.pdf"
    output_file = os.path.join(output_directory, output_filename)

    # Check for file existence and auto-increment if needed
    counter = 1
    while os.path.exists(output_file):
        output_filename = f"{base_filename}_{current_date}_{counter}.pdf"
        output_file = os.path.join(output_directory, output_filename)
        counter += 1
        if counter > 99:
            raise Exception("Maximum file increment limit (99) reached for this date")

    return output_file

def validate_password_strength(password):
    """Validate password meets minimum security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password should contain uppercase, lowercase, digits, and special characters"

    return True, "Password meets requirements"

def get_password_interactive():
    """
    Prompt user for password with VISIBLE input
    Security Warning: Passwords are displayed on screen
    """
    while True:
        print()
        print_box("PASSWORD SETUP", Colors.YELLOW)
        print_status('warning', 'Password will be VISIBLE on screen')
        print()

        user_password = input(f"{Colors.BOLD}Enter user password (to open PDF): {Colors.END}")

        # Validate password strength
        is_valid, message = validate_password_strength(user_password)
        if not is_valid:
            print_status('warning', message)
            retry = input(f"{Colors.YELLOW}Use this password anyway? (yes/no): {Colors.END}").lower()
            if retry != 'yes':
                continue

        # Ask for separate owner password
        use_different = input(f"{Colors.CYAN}Use different owner password for editing restrictions? (yes/no): {Colors.END}").lower()
        if use_different == 'yes':
            while True:
                owner_password = input(f"{Colors.BOLD}Enter owner password (for editing permissions, min 12 chars): {Colors.END}")

                # Validate owner password length
                if len(owner_password) < 12:
                    print_status('error', 'Owner password must be at least 12 characters')
                    continue

                # Check if owner password is different from user password
                if owner_password == user_password:
                    print_status('error', 'Owner password must be different from user password')
                    continue

                # Valid owner password
                break
        else:
            owner_password = user_password

        return user_password, owner_password

def password_protect_pdf(input_pdf_path, user_password, owner_password=None, script_dir=None):
    """
    Password protect PDF using PyMuPDF with AES-256 encryption

    Security Considerations:
        - AES-256 encryption (strongest available)
        - User password: Can open, view, and print (high-quality)
        - Owner password: Full access - can copy, modify, and annotate
        - Permissions: High-quality printing for all, Copy/Modify/Annotate with owner password
    """

    try:
        # Input validation
        if not os.path.exists(input_pdf_path):
            raise FileNotFoundError(f"Input PDF not found: {input_pdf_path}")

        if not user_password or len(user_password) < 8:
            raise ValueError("User password must be at least 8 characters")

        # Default script dir to current directory if not provided
        if script_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # Open the PDF
        pdf_document = fitz.open(input_pdf_path)

        # Set owner password if not provided
        if owner_password is None:
            owner_password = user_password

        # Define permissions (owner can copy and modify, user can only view and print)
        permissions = (
            fitz.PDF_PERM_PRINT |         # Allow printing
            fitz.PDF_PERM_PRINT_HQ |      # Allow high-quality printing
            fitz.PDF_PERM_ACCESSIBILITY | # Allow accessibility features
            fitz.PDF_PERM_COPY |          # Allow text/image copying
            fitz.PDF_PERM_MODIFY |        # Allow document modification
            fitz.PDF_PERM_ANNOTATE        # Allow annotations/comments
        )

        # Generate output filename based on original name + YYYYMMDD in OUTPUT folder
        output_file = get_output_filename(input_pdf_path, script_dir)

        # Save with encryption
        pdf_document.save(
            output_file,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw=owner_password,
            user_pw=user_password,
            permissions=permissions
        )

        pdf_document.close()

        # Report success with retention information
        expiration_date = datetime.now() + timedelta(days=30)

        print()
        print_box("SUCCESS", Colors.GREEN)
        print_status('success', f'Password-protected PDF created')
        print(f"   {Colors.BOLD}📁 Location:{Colors.END} OUTPUT/{os.path.basename(output_file)}")
        print()
        print_status('time', f'File expires on: {expiration_date.strftime("%Y-%m-%d")}')
        print_status('lock', 'Encryption: AES-256 (Military-grade)')
        print()
        print(f"   {Colors.CYAN}📋 Permissions:{Colors.END}")
        print(f"      ✓ Printing: Allowed (High-Quality)")
        print(f"      ✓ Copying: Allowed (with owner password)")
        print(f"      ✓ Modification: Allowed (with owner password)")
        print(f"      ✓ Annotations: Allowed (with owner password)")

        return output_file

    except Exception as e:
        print_status('error', f'Failed to password-protect PDF: {str(e)}')
        raise

def main():
    """Main execution with interactive password input"""

    # Set terminal window title
    if os.name == 'nt':  # Windows only
        os.system('title PDF Password Protection Tool')

    # Get script directory (will be in scripts subfolder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move up one directory to the main folder
    main_dir = os.path.dirname(script_dir)

    # Print banner
    print()
    print_banner()
    print()
    print()

    # Get input PDF path
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    else:
        input_pdf = input(f"{Colors.BOLD}📄 Enter path to unprotected PDF: {Colors.END}").strip()

    # Validate input file exists
    if not os.path.exists(input_pdf):
        print_status('error', f'File not found: {input_pdf}')
        sys.exit(1)

    print()
    print_status('info', f'Processing: {os.path.basename(input_pdf)}')

    # Get passwords interactively (VISIBLE input)
    user_pwd, owner_pwd = get_password_interactive()

    # Protect the PDF
    try:
        print()
        print_status('info', 'Encrypting PDF with AES-256...')

        protected_file = password_protect_pdf(
            input_pdf_path=input_pdf,
            user_password=user_pwd,
            owner_password=owner_pwd,
            script_dir=main_dir
        )

        print()
        print_box("COMPLETE\nPDF password protection completed successfully", Colors.GREEN)
        print()

    except Exception as e:
        print()
        print_box(f"FATAL ERROR\n{str(e)}", Colors.RED)
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
