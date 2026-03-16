import re
from backend.core.exceptions import PromptInjectionError
from data_ingestion.utils.logger import logger

class InputSanitizer:
    """Protège le système contre les entrées malveillantes ou invalides."""

    # Liste des pays autorisés pour le MVP
    ALLOWED_COUNTRIES = {"HTI", "DOM", "JAM", "CUB", "USA"}
    
    # Patterns suspects pour l'IA (Tentatives d'injection de prompt)
    SUSPICIOUS_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"ignore all rules",
        r"t'es un pirate"
    ]

    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """Nettoie et valide une question utilisateur."""
        if not query:
            return ""
        
        # 1. Vérification des injections
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Possible prompt injection detected: {query}")
                raise PromptInjectionError("Requête non autorisée pour des raisons de sécurité.")

        # 2. Nettoyage de base
        clean_query = query.strip()[:500] # Limite de taille
        return clean_query

    @classmethod
    def validate_country(cls, iso_code: str):
        """Valide un code pays contre la liste autorisée."""
        if iso_code.upper() not in cls.ALLOWED_COUNTRIES:
            logger.error(f"Invalid country access attempt: {iso_code}")
            raise ValueError(f"Code pays non supporté: {iso_code}")
        return iso_code.upper()
