import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from data_ingestion.utils.logger import logger

class DocumentProcessor:
    """Nettoyage, découpage et enrichissement des documents."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def clean_text(self, text: str) -> str:
        """Suppression du bruit (espaces multiples, sauts de ligne inutiles)."""
        # Suppression des espaces multiples et normalisation des sauts de ligne
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def process_pages(self, pages: List[Dict[str, Any]], global_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Prend des pages brutes, les nettoie, les découpe et ajoute des métadonnées.
        """
        chunks = []
        for page in pages:
            cleaned_text = self.clean_text(page["text"])
            if len(cleaned_text) < 50: # Ignore les pages quasi vides
                continue
            
            # Découpage de la page en chunks
            text_chunks = self.text_splitter.split_text(cleaned_text)
            
            for i, text in enumerate(text_chunks):
                metadata = {
                    "source": page["source_path"],
                    "page": page["page_number"],
                    "chunk_index": i
                }
                if global_metadata:
                    metadata.update(global_metadata)
                
                chunks.append({
                    "content": text,
                    "metadata": metadata
                })
                
        logger.info(f"Processed {len(pages)} pages into {len(chunks)} chunks.")
        return chunks
