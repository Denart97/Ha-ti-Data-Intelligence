from openai import OpenAI
from backend.core.config import settings
from .prompts import RESPONDER_PROMPT
from data_ingestion.utils.logger import logger

class AIResponder:
    """Générateur de réponses finales basées sur le contexte fourni."""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY missing. AIResponder running in Mock mode.")

    def generate_response(self, query: str, context: str) -> str:
        """Génère la synthèse finale avec citations."""
        logger.info("Generating final AI response...")
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": RESPONDER_PROMPT.format(context=context, query=query)},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"AI Call failed: {e}")
                # Fallback SILENCIEUX sur les données si l'API échoue
        
        # Logique de présentation des données (Professionnelle)
        response_parts = []
        if "--- DONNÉES STRUCTURELLES ---" in context:
            sql_part = context.split("--- DONNÉES STRUCTURELLES ---")[1].split("---")[0].strip()
            if sql_part and "None" not in sql_part:
                response_parts.append(f"📊 **Analyse Statistique :**\n{sql_part}")
        
        if "--- DOCUMENTS SOURCES ---" in context:
            rag_part = context.split("--- DOCUMENTS SOURCES ---")[1].strip()
            if rag_part and "[Aucun document trouvé" not in rag_part:
                response_parts.append(f"📄 **Contexte Documentaire :**\n{rag_part[:800]}...")
        
        if response_parts:
            return "\n\n".join(response_parts)
        
        return "Désolé, je n'ai pas trouvé assez de données pour répondre précisément à votre question. Veuillez vérifier l'ingestion documentaire."
