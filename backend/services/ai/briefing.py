from openai import OpenAI
from typing import Dict, Any
from backend.core.config import settings
from .prompts import BRIEFING_PROMPTS, BRIEFING_SYSTEM_TEMPLATE
from backend.services.analytics.engine import AnalyticsEngine
from backend.services.rag.retriever import DocumentRetriever
from sqlalchemy.orm import Session
from data_ingestion.utils.logger import logger

class BriefingService:
    """Service de génération de rapports et briefings profilés."""

    def __init__(self, db_session: Session):
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY missing. BriefingService running in Mock mode.")
        self.analytics = AnalyticsEngine(db_session)
        self.retriever = DocumentRetriever()

    def generate_briefing(self, profile: str, country_iso: str = "HTI") -> str:
        """Génère un briefing complet pour un profil spécifique."""
        logger.info(f"Generating briefing for profile: {profile}")
        
        if profile not in BRIEFING_PROMPTS:
            profile = "ANALYSTE" # Fallback
            
        # 1. Collecte de données analytiques (Exemples d'indicateurs clés)
        indicators = ["INFLATION", "GDP", "USD_HTG_REF"]
        data_context = "--- DONNÉES CLÉS ---\n"
        for ind in indicators:
            summary = self.analytics.generate_quantitative_summary(ind, country_iso)
            data_context += f"- {summary}\n"

        # 2. Collecte de contexte documentaire (RAG)
        logger.info("Fetching documentary context for briefing...")
        # On fait une recherche large sur la situation économique
        rag_results = self.retriever.search("Situation économique et sociale récente en Haïti", n_results=6)
        doc_context = "\n--- EXTRAITS DE RAPPORTS OFFICIELS ---\n"
        for res in rag_results:
            doc_context += f"Source: {res['metadata'].get('filename')} (P.{res['metadata'].get('page')})\n"
            doc_context += f"Contenu: {res['content']}\n\n"

        # 3. Envoi au LLM avec le prompt métier
        full_context = data_context + doc_context
        profile_instructions = BRIEFING_PROMPTS[profile]
        
        if not self.client:
            logger.warning("Mocking briefing because OpenAI client is unavailable.")
            return f"# Briefing Économique - Haïti ({profile})\n\n[MODE MOCK ACTIVÉ]\n\n{full_context}\n\n*Note: Ce briefing est basé sur une synthèse automatique des données brutes en l'absence de connexion au modèle LLM.*"

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": BRIEFING_SYSTEM_TEMPLATE.format(
                            profile_specific_instructions=profile_instructions,
                            context=full_context
                        )
                    },
                    {"role": "user", "content": f"Génère le briefing pour {country_iso}."}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Briefing generation failed: {e}")
            return "Échec de la génération du briefing."
