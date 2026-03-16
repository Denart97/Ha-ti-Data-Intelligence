from .query_router import QueryRouter
from .responder import AIResponder
from backend.services.rag.retriever import DocumentRetriever
from backend.services.sql.agent import SQLAgent

from data_ingestion.utils.logger import logger

class HybridOrchestrator:
    """Orchestrateur central pour le traitement hybride des requêtes."""

    def __init__(self):
        self.intent_router = QueryRouter()
        self.retriever = DocumentRetriever()
        self.responder = AIResponder()
        self.sql_agent = SQLAgent()

    def handle_query(self, query: str) -> Dict[str, Any]:
        """Traite une requête utilisateur de bout en bout."""
        logger.info(f"--- Processing New Query: {query} ---")
        
        # 1. Classification de l'intention
        intent = self.intent_router.classify(query)
        
        context_data = ""
        rag_results = []
        sql_results = None

        # 2. Exécution du pipeline selon l'intention
        if intent in ["RAG", "HYBRID"]:
            logger.info("Executing RAG Pipeline...")
            rag_results = self.retriever.search(query, n_results=4)
            if not rag_results:
                logger.warning("RAG returned no results (Mode dégradé).")
                context_data += "--- DOCUMENTS SOURCES ---\n[Aucun document trouvé ou service indisponible]\n\n"
            else:
                context_data += "--- DOCUMENTS SOURCES ---\n"
                for i, res in enumerate(rag_results, 1):
                    context_data += f"[{i}] Contenu: {res['content']}\n"
                    context_data += f"Source: {res['metadata'].get('filename')}, Page: {res['metadata'].get('page')}\n\n"

        if intent in ["SQL", "HYBRID"]:
            logger.info("Executing SQL Pipeline (Text-to-SQL)...")
            sql_results = self.sql_agent.execute_query(query)
            context_data += "--- DONNÉES STRUCTURELLES ---\n"
            context_data += f"{sql_results}\n\n"

        # 3. Génération de la réponse finale
        logger.info("Generating final response via Responder...")
        final_answer = self.responder.generate_response(query, context_data)

        # 4. Formattage du résultat final pour l'API
        return {
            "query": query,
            "intent": intent,
            "answer": final_answer,
            "sources": [
                {
                    "id": i+1,
                    "filename": res['metadata'].get('filename'),
                    "page": res['metadata'].get('page')
                } for i, res in enumerate(rag_results)
            ],
            "sql_context": sql_results
        }
