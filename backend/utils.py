# backend/utils.py
from pypdf import PdfReader
import io

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Takes the raw binary data of a PDF and converts it into a string of text.
    """
    # 1. Wrap the bytes in an 'io' object so the PDF reader can 'read' it like a file
    stream = io.BytesIO(file_content)
    pdf = PdfReader(stream)
    
    text = ""
    # 2. Loop through every page and pull the text out
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
            
    return text.strip()