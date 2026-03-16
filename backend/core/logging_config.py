import logging
import sys
from backend.core.config import settings

def setup_logging():
    """Configure le logging global pour l'application."""
    
    # Format de base
    log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    
    # Configuration racine
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("hdi_app.log", encoding='utf-8')
        ]
    )

    # Désactiver les logs trop verbeux des bibliothèques tierces
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logger = logging.getLogger("HDI_CORE")
    logger.info(f"Logging initialized at level {settings.LOG_LEVEL}")
    
    return logger

# Instance globale pour usage rapide
logger = setup_logging()
