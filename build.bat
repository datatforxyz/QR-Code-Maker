@echo off
echo Building QR Code Maker...
echo.

REM Check if Poetry is available
poetry --version >nul 2>&1
if errorlevel 1 (
    echo Error: Poetry is not installed or not in PATH
    echo Please install Poetry first: https://python-poetry.org/docs/#installation
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
poetry install --with dev

REM Run the build script
echo.
echo Running build script...
poetry run python build.py

echo.
echo Build process completed!
pause
