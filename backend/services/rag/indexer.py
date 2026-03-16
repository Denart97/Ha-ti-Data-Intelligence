import uuid
from typing import List, Dict, Any
from openai import OpenAI
from backend.core.config import settings
from backend.db.vector_store import vector_store
from data_ingestion.utils.logger import logger

class DocumentIndexer:
    """Indexation des chunks dans ChromaDB via OpenAI Embeddings."""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY missing. DocumentIndexer running in Mock mode.")
        self.collection = vector_store.get_collection()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings pour une liste de textes."""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=settings.EMBEDDING_MODEL
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI Embedding generation failed: {e}")
            raise

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexe une liste de chunks (content + metadata) dans ChromaDB."""
        if not chunks:
            return

        texts = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [str(uuid.uuid4()) for _ in chunks]

        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.get_embeddings(texts)

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully indexed {len(ids)} chunks into ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise
