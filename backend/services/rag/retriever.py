from typing import List, Dict, Any
from openai import OpenAI
from backend.core.config import settings
from backend.db.vector_store import vector_store
from data_ingestion.utils.logger import logger

class DocumentRetriever:
    """Récupération de chunks pertinents via recherche vectorielle."""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            logger.warning("OPENAI_API_KEY missing. DocumentRetriever running in Mock mode.")
        self.collection = vector_store.get_collection()

    def _get_query_embedding(self, query: str) -> List[float]:
        """Génère l'embedding de la requête utilisateur."""
        if not self.openai_client:
            logger.warning("Mocking embedding (zeros) because OpenAI client is unavailable.")
            return [0.0] * 1536 # Taille standard text-embedding-ada-002
            
        response = self.openai_client.embeddings.create(
            input=[query],
            model=settings.EMBEDDING_MODEL
        )
        return response.data[0].embedding

    def search(self, query: str, n_results: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recherche sémantique dans la banque documentaire.
        """
        logger.info(f"Searching for: '{query}' (filters: {filters})")
        
        query_embedding = self._get_query_embedding(query)
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filters
            )
            
            # Reconstruction du format de sortie
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
                
            return formatted_results
        except Exception as e:
            logger.error(f"Vector search failed (ChromaDB down?): {e}")
            # Mode dégradé : On retourne une liste vide pour permettre à l'orchestrateur de continuer
            return []
