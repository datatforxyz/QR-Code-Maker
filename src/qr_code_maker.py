import csv
import os
import textwrap
from io import BytesIO
from urllib.parse import urlparse
import string

import segno
from PIL import Image, ImageDraw, ImageFont


def clean_filename(text):
    """
    Cleans the text to create a valid filename by removing punctuation and unwanted characters.
    """
    return ''.join(c for c in text if c.isalnum() or c in (' ', '_', '-')).rstrip()


def clean_url(url):
    """
    Cleans the URL to create a valid filename by removing punctuation and unwanted characters.
    """
    parsed_url = urlparse(url)
    clean_path = parsed_url.path.strip('/').translate(str.maketrans('', '', string.punctuation))
    clean_netloc = parsed_url.netloc.translate(str.maketrans('', '', string.punctuation))
    return f"{clean_netloc}_{clean_path}".rstrip('_')



def get_font(font_path, font_size):
    """
    Retrieves the specified font, using default system font if none specified.
    """
    if font_path is None:
        # Use system default font
        return ImageFont.load_default()
    
    if not os.path.exists(font_path):
        print(f"Font not found at {font_path}. Using default system font.")
        return ImageFont.load_default()
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Failed to load font from {font_path}. Using default system font.")
        font = ImageFont.load_default()
    return font


def resample_filter():
    """
    Determines the appropriate resampling filter based on Pillow version.
    """
    try:
        # For Pillow >=10.0.0
        return Image.Resampling.LANCZOS
    except AttributeError:
        # For Pillow <10.0.0
        return Image.ANTIALIAS


def create_qr_code(url, qr_size=2000):
    """
    Generates a QR code using segno with a transparent background.
    """
    qr = segno.make(url, error='H')
    width, height = qr.symbol_size(scale=1)
    scale = qr_size // width
    scale = max(scale, 1)  # Ensure scale is at least 1
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=scale, dark='black', light=None, border=4)
    buffer.seek(0)
    img_qr = Image.open(buffer).convert('RGBA')
    return img_qr


def create_full_page_image(title, url, font_path, save_to_dir, page_size=(2550, 3300), dpi=300):
    """
    Creates a full-page image with the title at the top, a high-resolution QR code in the middle,
    and the URL text below the QR code, all on a transparent background.
    """
    # Create a transparent background image (Letter size at 300 DPI)
    img = Image.new('RGBA', page_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Define margins
    top_margin = 300
    side_margin = 300
    
    # Load fonts
    title_font_size = 150  # Increased font size for the title
    url_font_size = 80
    title_font = get_font(font_path, title_font_size)
    url_font = get_font(font_path, url_font_size)
    
    # Wrap the title text
    max_text_width = page_size[0] - 2 * side_margin
    wrapper = textwrap.TextWrapper(width=30)  # Adjust wrap width for larger font
    wrapped_title = wrapper.wrap(text=title)
    
    # Calculate total title height using getbbox
    total_title_height = 0
    line_heights = []
    for line in wrapped_title:
        bbox = title_font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_title_height += line_height + 20  # 20 pixels between lines
    total_title_height -= 20  # Remove extra spacing after last line
    
    # Position title
    current_y = top_margin
    for line in wrapped_title:
        bbox = title_font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        x_text = (page_size[0] - line_width) / 2
        draw.text((x_text, current_y), line, font=title_font, fill=(0, 0, 0, 255))  # Black text
        current_y += line_height + 20  # 20 pixels between lines
    
    # Generate QR code
    img_qr = create_qr_code(url, qr_size=2000)  # Adjust QR size as needed
    
    # Position QR code below the title, centered
    qr_x = (page_size[0] - img_qr.width) // 2
    qr_y = current_y + 100  # 100 pixels padding between title and QR
    
    # Add a border around the QR code
    border_size = 20  # Increased border size for visibility
    border_color = (0, 0, 0, 255)  # Black border
    
    # Create a new image for the bordered QR code
    bordered_qr_size = (img_qr.width + 2 * border_size, img_qr.height + 2 * border_size)
    bordered_qr = Image.new('RGBA', bordered_qr_size, border_color)
    bordered_qr.paste(img_qr, (border_size, border_size), img_qr)  # Use img_qr as mask for transparency
    
    img.paste(bordered_qr, (qr_x - border_size, qr_y - border_size), bordered_qr)
    
    # Update current_y to position URL below the QR code
    current_y = qr_y + bordered_qr.height + 100  # 100 pixels padding between QR and URL
    
    # Wrap the URL text
    wrapper = textwrap.TextWrapper(width=60)
    wrapped_url = wrapper.wrap(text=url)
    
    # Adjust font size to fit URL text within the width
    font_size = url_font_size
    while True:
        url_font = get_font(font_path, font_size)
        fits = True
        for line in wrapped_url:
            bbox = url_font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            if line_width > max_text_width and font_size > 40:
                fits = False
                break
        if fits or font_size <= 40:
            break
        font_size -= 2
        wrapped_url = wrapper.wrap(text=url)
    
    # Recalculate URL font after possible size reduction
    url_font = get_font(font_path, font_size)
    
    # Calculate total URL text height using getbbox
    total_url_height = 0
    url_line_heights = []
    for line in wrapped_url:
        bbox = url_font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        url_line_heights.append(line_height)
        total_url_height += line_height + 10  # 10 pixels between lines
    total_url_height -= 10  # Remove extra spacing after last line
    
    # Position URL
    for line in wrapped_url:
        bbox = url_font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        x_text = (page_size[0] - line_width) / 2
        draw.text((x_text, current_y), line, font=url_font, fill=(0, 0, 0, 255))  # Black text
        current_y += line_height + 10  # 10 pixels between lines
    
    return img


def process_csv(file_path, save_to_dir, font_path=""):
    """
    Processes a CSV file, generating a styled, high-resolution QR code image for each entry.
    
    Args:
        file_path (str): Path to the CSV file
        save_to_dir (str): Directory to save QR code images
        font_path (str): Path to font file (optional, will use default if empty)
    """
    if not os.path.exists(save_to_dir):
        os.makedirs(save_to_dir)
        print(f"Created directory: {save_to_dir}")
    
    # Use default font if none specified
    if not font_path:
        font_path = None
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        entries = list(reader)
    
    total_entries = len(entries)
    for index, entry in enumerate(entries, start=1):
        if len(entry) < 2:
            print(f"Skipping invalid entry ({index}/{total_entries}): {entry}")
            continue  # Skip invalid entries
        
        title, url = entry[0].strip(), entry[1].strip()
        if not url:
            print(f"Skipping entry with empty URL ({index}/{total_entries}): {title}")
            continue  # Skip entries without URL
        
        print(f"Processing ({index}/{total_entries}): {title} - {url}")
        img = create_full_page_image(title, url, font_path, save_to_dir)
        clean_title = clean_filename(title)
        filename = f"{clean_title}.png"
        img.save(os.path.join(save_to_dir, filename), format='PNG', dpi=(300, 300))
        print(f"Saved: {filename}")
    
    print("All QR codes have been created successfully.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate QR codes from CSV file")
    parser.add_argument("csv_file", help="Path to CSV file with title and URL columns")
    parser.add_argument("save_dir", nargs="?", default="output", 
                       help="Directory to save QR code images (default: output)")
    parser.add_argument("font_file", nargs="?", default="", 
                       help="Path to custom font file (optional)")
    
    args = parser.parse_args()
    
    process_csv(args.csv_file, args.save_dir, args.font_file)
