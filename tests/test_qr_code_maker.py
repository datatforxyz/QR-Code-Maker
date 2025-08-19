"""
Tests for the core QR code generation functionality.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PIL import Image
import segno

# Import the functions to test
from src.qr_code_maker import (
    clean_filename,
    clean_url,
    download_font,
    get_font,
    create_qr_code,
    create_full_page_image,
    process_csv
)


class TestCleanFilename:
    """Test filename cleaning functionality."""
    
    def test_clean_filename_basic(self):
        """Test basic filename cleaning."""
        assert clean_filename("Hello World") == "Hello World"
        assert clean_filename("Event 2024") == "Event 2024"
    
    def test_clean_filename_special_chars(self):
        """Test removal of special characters."""
        assert clean_filename("Event: Registration!") == "Event Registration"
        assert clean_filename("Survey@2024") == "Survey2024"
        assert clean_filename("File/Name\\") == "FileName"
    
    def test_clean_filename_unicode(self):
        """Test handling of unicode characters."""
        assert clean_filename("Café & Résumé") == "Café  Résumé"
        assert clean_filename("中文标题") == "中文标题"
    
    def test_clean_filename_edge_cases(self):
        """Test edge cases."""
        assert clean_filename("") == ""
        assert clean_filename("   ") == ""
        assert clean_filename("123") == "123"
        assert clean_filename("!@#$%^&*()") == ""


class TestCleanURL:
    """Test URL cleaning functionality."""
    
    def test_clean_url_basic(self):
        """Test basic URL cleaning."""
        result = clean_url("https://example.com/path")
        assert "example" in result
        assert "path" in result
    
    def test_clean_url_complex(self):
        """Test complex URL cleaning."""
        result = clean_url("https://sub.domain.com/path/to/page?param=value")
        assert "sub" in result
        assert "domain" in result
        assert "path" in result
        assert "page" in result
    
    def test_clean_url_special_chars(self):
        """Test URL with special characters."""
        result = clean_url("https://example.com/path-with-dashes")
        assert "path" in result
        assert "with" in result
        assert "dashes" in result


class TestFontHandling:
    """Test font downloading and loading functionality."""
    
    @patch('src.qr_code_maker.requests.get')
    def test_download_font_success(self, mock_get):
        """Test successful font download."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"fake_font_data"
        mock_get.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            download_font("https://example.com/font.ttf", temp_path)
            assert os.path.exists(temp_path)
            with open(temp_path, 'rb') as f:
                assert f.read() == b"fake_font_data"
        finally:
            os.unlink(temp_path)
    
    @patch('src.qr_code_maker.requests.get')
    def test_download_font_failure(self, mock_get):
        """Test font download failure."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            download_font("https://example.com/font.ttf", "nonexistent.ttf")
    
    @patch('src.qr_code_maker.download_font')
    def test_get_font_downloads_when_missing(self, mock_download):
        """Test that font is downloaded when missing."""
        mock_download.return_value = None
        
        with patch('os.path.exists', return_value=False):
            get_font("nonexistent.ttf", 12)
            mock_download.assert_called_once()


class TestQRCodeGeneration:
    """Test QR code generation functionality."""
    
    def test_create_qr_code_basic(self):
        """Test basic QR code creation."""
        url = "https://example.com"
        qr_img = create_qr_code(url, qr_size=1000)
        
        assert isinstance(qr_img, Image.Image)
        assert qr_img.mode == 'RGBA'
        assert qr_img.size[0] > 0
        assert qr_img.size[1] > 0
    
    def test_create_qr_code_different_sizes(self):
        """Test QR code creation with different sizes."""
        url = "https://example.com"
        
        small_qr = create_qr_code(url, qr_size=500)
        large_qr = create_qr_code(url, qr_size=2000)
        
        assert small_qr.size[0] < large_qr.size[0]
        assert small_qr.size[1] < large_qr.size[1]
    
    def test_create_qr_code_long_url(self):
        """Test QR code creation with long URLs."""
        long_url = "https://example.com/very/long/path/with/many/segments/and/parameters?param1=value1&param2=value2"
        qr_img = create_qr_code(long_url, qr_size=1000)
        
        assert isinstance(qr_img, Image.Image)
        assert qr_img.size[0] > 0
        assert qr_img.size[1] > 0


class TestImageGeneration:
    """Test full page image generation."""
    
    @patch('src.qr_code_maker.get_font')
    def test_create_full_page_image_basic(self, mock_get_font):
        """Test basic full page image creation."""
        # Mock font
        mock_font = MagicMock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)
        mock_get_font.return_value = mock_font
        
        title = "Test Event"
        url = "https://example.com"
        font_path = "test_font.ttf"
        save_dir = "test_output"
        
        img = create_full_page_image(title, url, font_path, save_dir)
        
        assert isinstance(img, Image.Image)
        assert img.mode == 'RGBA'
        assert img.size == (2480, 3508)  # Default A4 size
    
    @patch('src.qr_code_maker.get_font')
    def test_create_full_page_image_long_title(self, mock_get_font):
        """Test image creation with long title that needs wrapping."""
        # Mock font
        mock_font = MagicMock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)
        mock_get_font.return_value = mock_font
        
        long_title = "This is a very long title that should wrap to multiple lines when displayed in the QR code generator"
        url = "https://example.com"
        font_path = "test_font.ttf"
        save_dir = "test_output"
        
        img = create_full_page_image(long_title, url, font_path, save_dir)
        
        assert isinstance(img, Image.Image)
        assert img.size == (2480, 3508)


class TestCSVProcessing:
    """Test CSV file processing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_content = """Title,URL
Event Registration,https://example.com/register
Survey Link,https://example.com/survey
Website,https://example.com"""
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_process_csv_basic(self):
        """Test basic CSV processing."""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(self.csv_content)
        
        output_dir = os.path.join(self.temp_dir, "output")
        
        with patch('src.qr_code_maker.create_full_page_image') as mock_create:
            mock_img = MagicMock()
            mock_create.return_value = mock_img
            
            process_csv(csv_path, output_dir, "")
            
            # Should be called 3 times (once for each row)
            assert mock_create.call_count == 3
    
    def test_process_csv_invalid_entries(self):
        """Test CSV processing with invalid entries."""
        csv_content = """Title,URL
Event Registration,https://example.com/register
Invalid Entry
Survey Link,https://example.com/survey
,https://example.com/empty-title
Event No URL,"""
        
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        output_dir = os.path.join(self.temp_dir, "output")
        
        with patch('src.qr_code_maker.create_full_page_image') as mock_create:
            mock_img = MagicMock()
            mock_create.return_value = mock_img
            
            process_csv(csv_path, output_dir, "")
            
            # Should only process valid entries (1 valid out of 5)
            assert mock_create.call_count == 1
    
    def test_process_csv_creates_output_dir(self):
        """Test that output directory is created if it doesn't exist."""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(self.csv_content)
        
        output_dir = os.path.join(self.temp_dir, "new_output")
        
        with patch('src.qr_code_maker.create_full_page_image'):
            process_csv(csv_path, output_dir, "")
            
            assert os.path.exists(output_dir)


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_content = """Title,URL
Test Event,https://example.com/test"""
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('src.qr_code_maker.download_font')
    @patch('src.qr_code_maker.ImageFont.truetype')
    def test_end_to_end_workflow(self, mock_truetype, mock_download):
        """Test complete end-to-end workflow."""
        # Mock font system
        mock_font = MagicMock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)
        mock_truetype.return_value = mock_font
        mock_download.return_value = None
        
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(self.csv_content)
        
        output_dir = os.path.join(self.temp_dir, "output")
        
        # Run the complete process
        process_csv(csv_path, output_dir, "")
        
        # Verify output directory was created
        assert os.path.exists(output_dir)
        
        # Verify that the process completed without errors
        # (The actual image creation is mocked, so we just verify the flow)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_process_csv_nonexistent_file(self):
        """Test handling of nonexistent CSV file."""
        with pytest.raises(FileNotFoundError):
            process_csv("nonexistent.csv", "output", "")
    
    def test_process_csv_empty_file(self):
        """Test handling of empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            output_dir = tempfile.mkdtemp()
            try:
                process_csv(temp_path, output_dir, "")
                # Should complete without error (just no images generated)
            finally:
                shutil.rmtree(output_dir)
        finally:
            os.unlink(temp_path)
    
    def test_create_qr_code_empty_url(self):
        """Test handling of empty URL."""
        with pytest.raises(ValueError):
            create_qr_code("", qr_size=1000)
    
    def test_create_qr_code_invalid_url(self):
        """Test handling of invalid URL."""
        # This should still work as segno is quite forgiving
        qr_img = create_qr_code("not-a-url", qr_size=1000)
        assert isinstance(qr_img, Image.Image)


if __name__ == "__main__":
    pytest.main([__file__])
