import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.core.config import settings
from data_ingestion.utils.logger import logger

class VectorStore:
    """Manager pour ChromaDB."""

    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            self.collection_name = settings.COLLECTION_NAME
            self._available = True
        except Exception as e:
            logger.error(f"ChromaDB failed to initialize: {e}. Vector search will be disabled.")
            self.client = None
            self._available = False

    def get_collection(self):
        """Récupère ou crée la collection par défaut."""
        if not self._available or self.client is None:
            return None
        try:
            return self.client.get_or_create_collection(name=self.collection_name)
        except Exception as e:
            logger.error(f"Failed to get ChromaDB collection: {e}")
            return None

    def get_items_count(self) -> int:
        """Retourne le nombre d'éléments dans la collection."""
        collection = self.get_collection()
        return collection.count() if collection else 0

# Instance globale (ne crashe plus si ChromaDB absent)
try:
    vector_store = VectorStore()
except Exception as e:
    logger.error(f"VectorStore could not be initialized: {e}")
    vector_store = None
