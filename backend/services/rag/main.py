import os
import hashlib
from typing import List, Optional
from pathlib import Path
from backend.services.rag.loader import PDFLoader
from backend.services.rag.processor import DocumentProcessor
from backend.services.rag.indexer import DocumentIndexer
from data_ingestion.utils.logger import logger

class RAGPipeline:
    """Orchestrateur pour l'ingestion documentaire dans le vector store."""

    def __init__(self):
        self.loader = PDFLoader()
        self.processor = DocumentProcessor()
        self.indexer = DocumentIndexer()

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash SHA-256 d'un fichier pour éviter les doublons."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def ingest_directory(self, directory_path: str, tags: Optional[dict] = None):
        """
        Scanne un répertoire et ingère tous les PDFs trouvés.
        """
        logger.info(f"Scanning directory for PDFs: {directory_path}")
        path = Path(directory_path)
        
        pdf_files = list(path.glob("**/*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files.")

        for pdf_file in pdf_files:
            file_path = str(pdf_file.absolute())
            file_hash = self._calculate_file_hash(file_path)
            
            # Note: Dans une version avancée, on vérifierait ce hash en DB SQL 
            # avant de traiter pour éviter de ré-indexer inutilement.
            
            logger.info(f"Processing document: {pdf_file.name}")
            
            # 1. Extraction
            pages = self.loader.extract_text_with_pages(file_path)
            
            # 2. Transformation (Cleaning & Chunking)
            metadata = {
                "filename": pdf_file.name,
                "file_hash": file_hash
            }
            if tags:
                metadata.update(tags)
                
            chunks = self.processor.process_pages(pages, global_metadata=metadata)
            
            # 3. Indexation
            if chunks:
                self.indexer.index_chunks(chunks)
                logger.info(f"Ingestion complete for {pdf_file.name}")

if __name__ == "__main__":
    # Test local si exécuté en direct
    pipeline = RAGPipeline()
    # On crée un dossier data/raw_docs/ s'il n'existe pas pour les tests
    input_dir = "./data/raw_docs"
    os.makedirs(input_dir, exist_ok=True)
    
    pipeline.ingest_directory(input_dir)
