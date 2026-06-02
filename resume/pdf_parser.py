"""
PDF Resume Parser - Extract text from PDF resumes
"""

import pdfplumber
import PyPDF2
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def parse_pdf_resume(file_bytes: bytes) -> str:
    """
    Extract text from a PDF resume.
    
    Tries pdfplumber first (better for formatted PDFs), 
    falls back to PyPDF2.
    
    Returns extracted text string.
    """
    text = ""
    
    # Try pdfplumber first (handles tables and formatting better)
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
        
        if text.strip():
            return clean_text(text)
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
    
    # Fallback to PyPDF2
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        text = "\n".join(pages_text)
        return clean_text(text)
    except Exception as e:
        logger.error(f"PyPDF2 also failed: {e}")
        return ""


def clean_text(text: str) -> str:
    """Clean extracted text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    
    return text


def get_pdf_metadata(file_bytes: bytes) -> dict:
    """Extract PDF metadata."""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        info = reader.metadata
        return {
            "num_pages": len(reader.pages),
            "title": info.get("/Title", ""),
            "author": info.get("/Author", ""),
        }
    except Exception as e:
        logger.error(f"Metadata extraction error: {e}")
        return {"num_pages": 0}