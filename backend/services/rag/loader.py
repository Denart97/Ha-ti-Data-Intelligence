import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
from data_ingestion.utils.logger import logger

class PDFLoader:
    """Chargeur de documents PDF pour l'extraction de texte."""

    @staticmethod
    def extract_text_with_pages(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extrait le texte page par page d'un PDF.
        Retourne une liste de dicts : [{"page": 1, "text": "...", "metadata": {...}}]
        """
        path = Path(pdf_path)
        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return []

        pages_content = []
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                pages_content.append({
                    "page_number": page_num,
                    "text": text,
                    "source_path": str(path.absolute())
                })
            doc.close()
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path}: {e}")
            
        return pages_content
