"""
File Parser Utility Module
Handles extraction of text content from various file formats.

Currently supports:
- PDF documents (.pdf)
"""

from pypdf import PdfReader  # Library for reading PDF files


def pdf_parsing(file):
    """
    Extract all text content from a PDF file.
    
    Reads through all pages of a PDF document and concatenates
    the text into a single string.
    
    Args:
        file: File object (can be uploaded file or file path)
              Must be a valid PDF file
        
    Returns:
        str: Extracted text content from all pages
        
    Example:
        with open("document.pdf", "rb") as f:
            text = pdf_parsing(f)
            print(text)  # "Page 1 content... Page 2 content..."
    """
    # Create PDF reader object
    reader = PdfReader(file)

    # Initialize empty string to store all text
    file_content = ""
    
    # Loop through each page and extract text
    for page in reader.pages:
        file_content += page.extract_text()  # Append page text to result

    return file_content


