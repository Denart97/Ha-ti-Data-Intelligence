from backend.core.config import settings
from data_ingestion.utils.logger import logger

class QueryRouter:
    """Classifie les requêtes utilisateur (Version simplifiée)."""

    def __init__(self):
        self.client = None
        logger.warning("QueryRouter: Mode Simplifié activé.")

    def classify(self, query: str) -> str:
        return "HYBRID"
