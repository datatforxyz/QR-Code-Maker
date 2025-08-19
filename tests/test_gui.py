"""
Tests for the GUI functionality.
"""

import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
import tempfile
import os
import shutil

# Import the GUI class
from src.main import QRCodeMakerGUI


class TestGUIInitialization:
    """Test GUI initialization and setup."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_gui_initialization(self):
        """Test that GUI initializes correctly."""
        app = QRCodeMakerGUI(self.root)
        
        # Check that variables are initialized
        assert app.csv_file_path.get() == ""
        assert app.save_directory.get() == "output"
        assert app.font_file_path.get() == "DejaVuSans.ttf"
        assert app.use_custom_font.get() == False
    
    def test_gui_title(self):
        """Test that GUI has correct title."""
        app = QRCodeMakerGUI(self.root)
        assert self.root.title() == "QR Code Maker"
    
    def test_gui_geometry(self):
        """Test that GUI has reasonable dimensions."""
        app = QRCodeMakerGUI(self.root)
        geometry = self.root.geometry()
        width, height = map(int, geometry.split('x'))
        assert width >= 600
        assert height >= 500


class TestGUIFunctionality:
    """Test GUI functionality and user interactions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.app = QRCodeMakerGUI(self.root)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir)
    
    def test_browse_csv(self):
        """Test CSV file browsing functionality."""
        with patch('tkinter.filedialog.askopenfilename') as mock_askopenfilename:
            mock_askopenfilename.return_value = "/path/to/test.csv"
            self.app.browse_csv()
            
            assert self.app.csv_file_path.get() == "/path/to/test.csv"
    
    def test_browse_save_dir(self):
        """Test save directory browsing functionality."""
        with patch('tkinter.filedialog.askdirectory') as mock_askdirectory:
            mock_askdirectory.return_value = "/path/to/output"
            self.app.browse_save_dir()
            
            assert self.app.save_directory.get() == "/path/to/output"
    
    def test_browse_font(self):
        """Test font file browsing functionality."""
        with patch('tkinter.filedialog.askopenfilename') as mock_askopenfilename:
            mock_askopenfilename.return_value = "/path/to/font.ttf"
            self.app.browse_font()
            
            assert self.app.font_file_path.get() == "/path/to/font.ttf"
    
    def test_toggle_font_field(self):
        """Test font field toggle functionality."""
        # Initially disabled
        assert self.app.font_file_path.get() == "DejaVuSans.ttf"
        
        # Enable custom font
        self.app.use_custom_font.set(True)
        self.app.toggle_font_field()
        assert self.app.font_file_path.get() == ""
        
        # Disable custom font
        self.app.use_custom_font.set(False)
        self.app.toggle_font_field()
        assert self.app.font_file_path.get() == "DejaVuSans.ttf"


class TestGUIValidation:
    """Test GUI input validation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.app = QRCodeMakerGUI(self.root)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir)
    
    def test_validate_inputs_no_csv(self):
        """Test validation when no CSV file is selected."""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            result = self.app.validate_inputs()
            
            assert result == False
            mock_showerror.assert_called_once()
    
    def test_validate_inputs_nonexistent_csv(self):
        """Test validation when CSV file doesn't exist."""
        self.app.csv_file_path.set("/nonexistent/file.csv")
        
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            result = self.app.validate_inputs()
            
            assert result == False
            mock_showerror.assert_called_once()
    
    def test_validate_inputs_valid_inputs(self):
        """Test validation with valid inputs."""
        # Create a temporary CSV file
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        self.app.save_directory.set(self.temp_dir)
        
        result = self.app.validate_inputs()
        assert result == True
    
    def test_validate_inputs_creates_output_dir(self):
        """Test that output directory is created if it doesn't exist."""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        
        # Set output directory to a new path
        new_output_dir = os.path.join(self.temp_dir, "new_output")
        self.app.save_directory.set(new_output_dir)
        
        result = self.app.validate_inputs()
        assert result == True
        assert os.path.exists(new_output_dir)


class TestGUIProcessing:
    """Test GUI processing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.app = QRCodeMakerGUI(self.root)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir)
    
    @patch('src.main.process_csv')
    def test_process_qr_codes_success(self, mock_process_csv):
        """Test successful QR code processing."""
        # Set up valid inputs
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        self.app.save_directory.set(self.temp_dir)
        
        # Mock the processing to complete successfully
        mock_process_csv.return_value = None
        
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            self.app.process_qr_codes()
            
            # Wait for the thread to complete
            self.root.after(100, self.root.quit)
            self.root.mainloop()
            
            # Check that success message was shown
            mock_showinfo.assert_called_once()
    
    @patch('src.main.process_csv')
    def test_process_qr_codes_failure(self, mock_process_csv):
        """Test QR code processing failure."""
        # Set up valid inputs
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        self.app.save_directory.set(self.temp_dir)
        
        # Mock the processing to fail
        mock_process_csv.side_effect = Exception("Processing failed")
        
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.app.process_qr_codes()
            
            # Wait for the thread to complete
            self.root.after(100, self.root.quit)
            self.root.mainloop()
            
            # Check that error message was shown
            mock_showerror.assert_called_once()
    
    def test_process_qr_codes_validation_failure(self):
        """Test that processing doesn't start with invalid inputs."""
        with patch('src.main.process_csv') as mock_process_csv:
            self.app.process_qr_codes()
            
            # Should not call process_csv due to validation failure
            mock_process_csv.assert_not_called()


class TestGUIThreading:
    """Test GUI threading behavior."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.app = QRCodeMakerGUI(self.root)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir)
    
    def test_processing_disables_ui(self):
        """Test that UI is disabled during processing."""
        # Set up valid inputs
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        self.app.save_directory.set(self.temp_dir)
        
        # Start processing
        self.app.process_qr_codes()
        
        # Check that button is disabled
        assert self.app.process_button.cget('state') == 'disabled'
        
        # Check that progress bar is running
        # Note: We can't easily test the progress bar state in a unit test
        # but we can verify the method was called
    
    def test_processing_completes_ui_restoration(self):
        """Test that UI is restored after processing completes."""
        # Set up valid inputs
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        self.app.save_directory.set(self.temp_dir)
        
        with patch('src.main.process_csv'):
            # Start processing
            self.app.process_qr_codes()
            
            # Simulate completion
            self.app._processing_complete(True, "Success!")
            
            # Check that button is re-enabled
            assert self.app.process_button.cget('state') == 'normal'


class TestGUIIntegration:
    """Integration tests for GUI functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.app = QRCodeMakerGUI(self.root)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.root.destroy()
        shutil.rmtree(self.temp_dir)
    
    def test_gui_creates_directories(self):
        """Test that GUI creates necessary directories."""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f:
            f.write("Title,URL\nTest,https://example.com")
        
        self.app.csv_file_path.set(csv_path)
        
        # Set output directory to a new path
        new_output_dir = os.path.join(self.temp_dir, "new_output")
        self.app.save_directory.set(new_output_dir)
        
        # Validate inputs (this should create the directory)
        result = self.app.validate_inputs()
        assert result == True
        assert os.path.exists(new_output_dir)


if __name__ == "__main__":
    pytest.main([__file__])
