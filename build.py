#!/usr/bin/env python3
"""
Build script for QR Code Maker using PyInstaller.
Creates a single executable file for distribution.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False


def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    print("Cleaning previous build artifacts...")
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"✓ Removed {file_path}")


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n" + "="*50)
    print("Building QR Code Maker Executable")
    print("="*50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # PyInstaller command for single file
    pyinstaller_cmd = [
        'pyinstaller',
        '--onefile',                    # Create single executable
        '--windowed',                   # Hide console window (for GUI)
        '--name=QRCodeMaker',           # Executable name
        '--icon=icon.ico',              # Icon file (if exists)
        '--add-data=src;src',           # Include source directory
        '--hidden-import=PIL._tkinter_finder',  # Include PIL tkinter support
        '--hidden-import=tkinter',      # Include tkinter
        '--hidden-import=tkinter.ttk',  # Include ttk
        '--hidden-import=tkinter.filedialog',  # Include filedialog
        '--hidden-import=tkinter.messagebox',  # Include messagebox
        '--clean',                       # Clean cache
        'src/main.py'                   # Main script to build
    ]
    
    # Remove icon if it doesn't exist
    if not os.path.exists('icon.ico'):
        pyinstaller_cmd.remove('--icon=icon.ico')
    
    # Run PyInstaller
    if not run_command(pyinstaller_cmd, "PyInstaller build"):
        print("Build failed!")
        return False
    
    print("\n" + "="*50)
    print("Build completed successfully!")
    print("="*50)
    
    # Show output information
    dist_dir = Path('dist')
    if dist_dir.exists():
        exe_files = list(dist_dir.glob('*.exe'))
        if exe_files:
            exe_path = exe_files[0]
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"File size: {size_mb:.1f} MB")
            print(f"Location: {exe_path.absolute()}")
    
    return True


def build_command_line():
    """Build command-line version only"""
    print("\n" + "="*50)
    print("Building Command-Line Version")
    print("="*50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # PyInstaller command for command-line version
    pyinstaller_cmd = [
        'pyinstaller',
        '--onefile',                    # Create single executable
        '--name=QRCodeMakerCLI',       # Executable name
        '--add-data=src;src',          # Include source directory
        '--clean',                      # Clean cache
        'src/qr_code_maker.py'         # Command-line script to build
    ]
    
    # Run PyInstaller
    if not run_command(pyinstaller_cmd, "PyInstaller build (CLI)"):
        print("CLI build failed!")
        return False
    
    print("\n" + "="*50)
    print("CLI build completed successfully!")
    print("="*50)
    
    return True


def main():
    """Main build function"""
    print("QR Code Maker Build Script")
    print("="*50)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found. Please install it first:")
        print("  poetry install --with dev")
        return False
    
    # Check if source files exist
    if not os.path.exists('src/main.py'):
        print("✗ src/main.py not found. Please ensure the source files are in the src/ directory.")
        return False
    
    if not os.path.exists('src/qr_code_maker.py'):
        print("✗ src/qr_code_maker.py not found. Please ensure the source files are in the src/ directory.")
        return False
    
    # Build options
    print("\nBuild options:")
    print("1. GUI Application (main.py)")
    print("2. Command-Line Tool (qr_code_maker.py)")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        return build_executable()
    elif choice == "2":
        return build_command_line()
    elif choice == "3":
        success1 = build_executable()
        success2 = build_command_line()
        return success1 and success2
    else:
        print("Invalid choice. Please run the script again.")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 All builds completed successfully!")
        print("You can find the executables in the 'dist' directory.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")
        sys.exit(1)
