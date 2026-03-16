import pytest
from backend.services.analytics.engine import AnalyticsEngine
from data_ingestion.core.models import DataPoint

def test_generate_indicator_trend_empty(db_session):
    """Vérifie que le moteur gère correctement l'absence de données."""
    engine = AnalyticsEngine(db_session)
    result = engine.get_indicator_trend("INEXISTANT", "HTI")
    
    assert "series" in result
    assert len(result["series"]) == 0

def test_quantitative_summary_formatting():
    """Vérifie le formatage des résumés pour l'IA (Mock context)."""
    # Ce test pourrait vérifier la logique de calcul de variation
    # Pour le moment, on teste la structure de base
    from backend.services.analytics.engine import AnalyticsEngine
    from unittest.mock import MagicMock
    
    mock_db = MagicMock()
    engine = AnalyticsEngine(mock_db)
    
    summary = engine.generate_quantitative_summary("INFLATION", "HTI")
    assert isinstance(summary, str)
    assert "HTI" in summary
