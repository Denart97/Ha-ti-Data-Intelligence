from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.pg_session import get_db
from backend.db.vector_store import vector_store
from backend.core.logging_config import logger

monitoring_router = APIRouter(prefix="/monitoring", tags=["System Monitoring"])

@monitoring_router.get("/health/full")
async def full_health_check(db: Session = Depends(get_db)):
    """Vérification exhaustive de la santé du système."""
    
    status = {
        "api": "online",
        "database": "offline",
        "vector_store": "offline",
        "overall": "degraded"
    }

    # 1. Test PostgreSQL
    try:
        db.execute("SELECT 1")
        status["database"] = "connected"
    except Exception as e:
        logger.error(f"HealthCheck: Database failure: {e}")

    # 2. Test ChromaDB
    try:
        count = vector_store.get_items_count()
        status["vector_store"] = f"connected ({count} chunks)"
    except Exception as e:
        logger.error(f"HealthCheck: VectorStore failure: {e}")

    # Résultat global
    if status["database"] == "connected" and "connected" in status["vector_store"]:
        status["overall"] = "healthy"

    return status

@monitoring_router.get("/stats")
async def get_system_stats():
    """Retourne des statistiques sommaires d'utilisation (Simulé pour MVP)."""
    return {
        "uptime": "99.9%",
        "daily_queries": 150,
        "active_sources": ["WorldBank", "FMI", "BRH"],
        "last_ingestion": "2026-03-16T12:00:00Z"
    }
