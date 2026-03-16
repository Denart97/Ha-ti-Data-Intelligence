from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import settings

# Création de l'engine SQLAlchemy
engine = create_engine(settings.DATABASE_URL, echo=False)

# Création de la factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ORM
Base = declarative_base()

def get_db():
    """Dépendance pour obtenir une session de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
