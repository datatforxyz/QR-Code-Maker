# QR Code Maker Makefile
# Provides convenient commands for development and building

.PHONY: help install run-gui run-cli build build-gui build-cli clean test format lint install-dev

# Default target
help:
	@echo "QR Code Maker - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install all dependencies including dev tools"
	@echo "  run-gui      - Run the GUI application"
	@echo "  run-cli      - Run the command-line tool with demo data"
	@echo ""
	@echo "Building:"
	@echo "  build        - Build both GUI and CLI executables"
	@echo "  build-gui    - Build only the GUI executable"
	@echo "  build-cli    - Build only the CLI executable"
	@echo ""
	@echo "Code Quality:"
	@echo "  test         - Run tests"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run linting with flake8"
	@echo "  type-check   - Run type checking with mypy"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  clean-all    - Clean everything including virtual environment"
	@echo ""

# Installation
install:
	@echo "Installing production dependencies..."
	poetry install --only main

install-dev:
	@echo "Installing all dependencies including dev tools..."
	poetry install --with dev

# Running the application
run-gui:
	@echo "Starting QR Code Maker GUI..."
	poetry run python src/main.py

run-cli:
	@echo "Running QR Code Maker CLI with demo data..."
	@if [ -f "demo.csv" ]; then \
		poetry run python src/qr_code_maker.py demo.csv; \
	else \
		echo "Creating demo.csv with sample data..."; \
		echo "Title,URL" > demo.csv; \
		echo "Event Registration,https://example.com/register" >> demo.csv; \
		echo "Survey Link,https://example.com/survey" >> demo.csv; \
		echo "Website,https://example.com" >> demo.csv; \
		poetry run python src/qr_code_maker.py demo.csv; \
	fi

# Building executables
build: build-gui build-cli
	@echo "🎉 All builds completed successfully!"

build-gui:
	@echo "Building GUI executable..."
	poetry run python build.py
	@echo "GUI executable built successfully!"

build-cli:
	@echo "Building CLI executable..."
	poetry run pyinstaller --onefile --name=QRCodeMakerCLI src/qr_code_maker.py
	@echo "CLI executable built successfully!"

# Code quality
test:
	@echo "Running tests..."
	poetry run pytest

format:
	@echo "Formatting code with black..."
	poetry run black src/ build.py

lint:
	@echo "Running linting with flake8..."
	poetry run flake8 src/ build.py

type-check:
	@echo "Running type checking with mypy..."
	poetry run mypy src/ build.py

# Cleaning
clean:
	@echo "Cleaning build artifacts and cache..."
	@rm -rf build/ dist/ __pycache__/ .pytest_cache/ .mypy_cache/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup completed!"

clean-all: clean
	@echo "Removing virtual environment..."
	poetry env remove python
	@echo "Full cleanup completed!"

# Windows-specific commands
ifeq ($(OS),Windows_NT)
run-gui-windows:
	@echo "Starting QR Code Maker GUI (Windows)..."
	poetry run python src\main.py

build-windows:
	@echo "Building on Windows..."
	build.bat

clean-windows:
	@echo "Cleaning on Windows..."
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@del /q *.pyc 2>nul || echo No .pyc files to remove
	@echo "Windows cleanup completed!"
endif

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "You can now run: make run-gui"

quick-build: clean build
	@echo "Quick build completed!"

# Demo data
demo-data:
	@echo "Creating demo CSV file..."
	@echo "Title,URL" > demo.csv
	@echo "Event Registration,https://example.com/register" >> demo.csv
	@echo "Survey Link,https://example.com/survey" >> demo.csv
	@echo "Website,https://example.com" >> demo.csv
	@echo "Demo data created in demo.csv"

# Check system
check-system:
	@echo "Checking system requirements..."
	@echo "Python version:"
	@python --version
	@echo "Poetry version:"
	@poetry --version
	@echo "System: $(shell uname -s)"
	@echo "Architecture: $(shell uname -m)"

# Default target when no arguments provided
.DEFAULT_GOAL := help
