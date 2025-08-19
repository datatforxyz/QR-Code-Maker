# QR Code Maker

A Python tool to generate high-resolution QR codes with titles and URLs. Features both a GUI interface and command-line tools for batch processing CSV files.

## Quick Start

```bash
# Install dependencies
make install-dev

# Run the GUI application
make run-gui

# Build executables
make build
```

## Makefile Commands

### **Development:**
- `make install` - Install production dependencies
- `make install-dev` - Install all dependencies including dev tools
- `make run-gui` - Run the GUI application
- `make run-cli` - Run the command-line tool with demo data
- `make dev-setup` - Complete development environment setup

### **Building:**
- `make build` - Build both GUI and CLI executables
- `make build-gui` - Build only the GUI executable
- `make build-cli` - Build only the CLI executable
- `make quick-build` - Clean and build everything

### **Code Quality:**
- `make test` - Run tests
- `make format` - Format code with black
- `make lint` - Run linting with flake8
- `make type-check` - Run type checking with mypy

### **Maintenance:**
- `make clean` - Clean build artifacts and cache
- `make clean-all` - Clean everything including virtual environment
- `make demo-data` - Create sample CSV file for testing

### **System:**
- `make check-system` - Check system requirements
- `make help` - Show all available commands (default)

## CSV Format

Your CSV file must have exactly two columns: `Title` and `URL`.

```csv
Title,URL
"Event Registration","https://example.com/register"
"Survey Link","https://example.com/survey"
"Website","https://example.com"
"Conference 2024","https://conference.example.com"
```

### CSV Requirements:
- **Header row**: Must include "Title" and "URL" columns
- **Title**: Any text (will be displayed above the QR code)
- **URL**: Valid URL (will be encoded in the QR code)
- **Encoding**: UTF-8 recommended for international characters
- **Quotes**: Optional but recommended for titles with commas

### Example Use Cases:
- Event registration links
- Survey forms
- Website URLs
- Social media profiles
- Contact information
- Product pages

## GUI Features

The GUI application provides:
- **Single QR Code**: Enter title and URL directly
- **Batch Processing**: Select CSV file for multiple QR codes
- **Custom Fonts**: Optional custom font selection
- **Output Directory**: Choose where to save generated images
- **Progress Tracking**: Visual feedback during processing

## Command Line Usage

```bash
# Single QR code
python src/qr_code_maker.py "Event Title" "https://example.com"

# Batch processing with CSV
python src/qr_code_maker.py input.csv output_folder

# With custom font
python src/qr_code_maker.py input.csv output_folder custom_font.ttf
```

## Output

- **Format**: High-resolution PNG images (300 DPI)
- **Size**: Letter page layout (2550x3300 pixels)
- **Content**: Title, QR code, and URL text
- **Background**: Transparent (perfect for printing)
- **Naming**: Cleaned title text used for filenames

## Requirements

- Python 3.11+
- Poetry (for dependency management)
- Windows/Linux/macOS supported
