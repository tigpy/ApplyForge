"""
Document Extraction Service for ApplyForge (PyMuPDF and python-docx)
"""
from pathlib import Path
from typing import Optional
from packages.shared.logger import logger

class DocumentExtractor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extracts plain text from PDF using PyMuPDF (fitz) with fallback."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(p))
            text_blocks = []
            for page in doc:
                text_blocks.append(page.get_text())
            doc.close()
            return "\n".join(text_blocks).strip()
        except ImportError:
            logger.warning("PyMuPDF (fitz) not available, attempting simple extraction")
            with open(p, "rb") as f:
                content = f.read()
            # Basic fallback
            return content.decode("utf-8", errors="ignore")

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extracts plain text from Word (.docx) files using python-docx."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            import docx
            doc = docx.Document(str(p))
            full_text = [para.text for para in doc.paragraphs if para.text]
            return "\n".join(full_text).strip()
        except ImportError:
            logger.warning("python-docx not available")
            return ""

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Auto-detects format and extracts clean text."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(file_path)
        elif ext in (".docx", ".doc"):
            return cls.extract_text_from_docx(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
