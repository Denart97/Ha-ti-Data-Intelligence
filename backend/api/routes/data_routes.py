from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from backend.db.pg_session import get_db
from backend.services.analytics.engine import AnalyticsEngine
from backend.models.sql_models import Dataset
import os
import json
import re

data_router = APIRouter(prefix="/data", tags=["Macroeconomic Data"])

@data_router.get("/indicator-trend")
async def get_trend(indicator_code: str, country_iso: str, db: Session = Depends(get_db)):
    """Récupère la tendance et les stats d'un indicateur pour un pays."""
    engine = AnalyticsEngine(db)
    series = engine.get_time_series(indicator_code, country_iso)
    stats = engine.calculate_stats(series)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No data found for this combination.")
        
    return {
        "series": series,
        "analytics": stats
    }

@data_router.get("/dataset-status")
async def get_status(db: Session = Depends(get_db)):
    """Retourne l'état de fraîcheur des sources."""
    results = db.query(Dataset).limit(10).all()
    return [
        {
            "dataset": d.code_dataset,
            "frequence": d.frequence_maj,
            "url": d.url_origine
        } for d in results
    ]

@data_router.post("/refresh-brh")
async def refresh_brh():
    """Lance un crawl et ingestion BRH en mode supervisé. Nécessite backend local en marche."""
    try:
        from data_ingestion.extractors.brh.extractor import BRHExtractor
        from data_ingestion.core.persistence import IngestionRepository
        from backend.db.pg_session import SessionLocal
        from data_ingestion.core.validator import DataValidator

        brh = BRHExtractor()
        indicators = ["USD_HTG_REF", "EUR_HTG", "CPI_HTI", "RESERVES_HTI", "M3_HTI", "BONS_BRH", "BALANCE_PAIEMENTS", "DEFICIT_BUDGET"]
        data_points = brh.fetch_data(indicators, ["HTI"])

        db = SessionLocal()
        try:
            repository = IngestionRepository(db)
            validated = DataValidator.validate(data_points)
            repository.save_data_points(validated)
        finally:
            db.close()

        return {"status": "ok", "count": len(validated), "message": "BRH data refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@data_router.get('/brh-indicators')
async def list_brh_indicators():
    """Retourne la liste d'indicateurs découverts par le crawler BRH (métadonnées locales)."""
    try:
        path = os.path.join('data_ingestion', 'extractors', 'brh', 'crawl_metadata.json')
        if not os.path.exists(path):
            return {"indicators": []}

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            indicators = set()
            # support both list-of-resources or dict with 'resources' key
            resources = data if isinstance(data, list) else data.get('resources', [])
            for r in resources:
                title = (r.get('title') if isinstance(r, dict) else '') or ''
                # split heuristically on common separators, keep words longer than 2
                for part in re.split('[,;/|\\-]', title):
                    p = part.strip()
                    if len(p) > 2:
                        indicators.add(p)

        return {"indicators": sorted(indicators)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
