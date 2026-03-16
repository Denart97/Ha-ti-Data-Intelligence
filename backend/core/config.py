import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Configuration centralisée de l'application."""
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./haiti_data.db"
    
    # LLM & IA
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector Store
    CHROMA_DB_PATH: str = "./data/chroma_db"
    COLLECTION_NAME: str = "hadi_docs"
    
    # Extraction & Tâches
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Sécurité
    API_KEY_HDI: Optional[str] = "dev-secret-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instance unique de config
settings = Settings()
