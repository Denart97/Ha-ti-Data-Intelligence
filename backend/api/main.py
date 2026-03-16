from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.ai_routes import ai_router
from backend.api.routes.monitoring_routes import monitoring_router
from backend.api.routes.data_routes import data_router
from backend.api.middleware.logging_middleware import LoggingMiddleware
from backend.core.config import settings
from backend.core.logging_config import logger
from backend.services.analytics.engine import AnalyticsEngine
from backend.db.pg_session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

app = FastAPI(
    title="Haiti Data Intelligence API",
    description="Backend analytique et IA (RAG/SQL) pour l'économie d'Haïti.",
    version="1.0.0"
)

# Enregistrement du Middleware de Logging (Observabilité)
app.add_middleware(LoggingMiddleware)

# Configuration CORS pour le frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(ai_router)
app.include_router(monitoring_router)
app.include_router(data_router)

from backend.schemas.api_schemas import ComparisonRequest
from backend.models.sql_models import Dataset

@app.get("/data/indicator-trend", tags=["Macroeconomic Data"])
async def get_trend_direct(indicator_code: str, country_iso: str, db: Session = Depends(get_db)):
    engine = AnalyticsEngine(db)
    series = engine.get_time_series(indicator_code, country_iso)
    if not series:
        raise HTTPException(status_code=404, detail="No data found")
    stats = engine.calculate_stats(series)
    return {"series": series, "analytics": stats}

@app.post("/data/compare", tags=["Macroeconomic Data"])
async def compare_direct(request: ComparisonRequest, db: Session = Depends(get_db)):
    engine = AnalyticsEngine(db)
    if not request.indicators:
        raise HTTPException(status_code=400, detail="At least one indicator code is required.")
    return engine.compare_countries(request.indicators[0], request.countries)

@app.get("/data/dataset-status", tags=["Macroeconomic Data"])
async def get_status_direct(db: Session = Depends(get_db)):
    results = db.query(Dataset).limit(10).all()
    return [{"dataset": d.code_dataset, "frequence": d.frequence_maj, "url": d.url_origine} for d in results]

@app.get("/", tags=["Root"])
async def root():
    routes = [{"path": r.path, "name": r.name} for r in app.routes]
    return {"message": "Welcome to Haiti Data Intelligence API", "routes": routes}

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Vérifie la santé de l'API et des dépendances."""
    # Simulation d'une vérification de DB
    # TODO: Ajouter ping vers PostgreSQL et ChromaDB
    return {
        "status": "healthy",
        "api": "up",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Launching FastAPI Server...")
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
