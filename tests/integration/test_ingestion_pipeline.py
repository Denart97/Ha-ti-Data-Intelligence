import pytest
from data_ingestion.extractors.wb.client import WBClient
from data_ingestion.core.repository import DataRepository
from data_ingestion.core.validator import DataValidator
from data_ingestion.core.models import DataPoint

def test_ingestion_flow_wb_mock(db_session, mocker):
    """Vérifie le flux complet d'ingestion avec un mock de l'API Banque Mondiale."""
    
    # 1. Setup Mock Data
    mock_data = [
        {"indicator": {"id": "GDP"}, "country": {"id": "HTI"}, "date": "2023", "value": 1.2}
    ]
    mocker.patch("requests.get").return_value.json.return_value = [{}, mock_data]
    
    # 2. Execution du pipeline
    wb_client = WBClient()
    raw_data = wb_client.fetch_data({"GDP": "NY.GDP.MKTP.KD.ZG"}, ["HTI"])
    
    validated_data = DataValidator.validate(raw_data)
    
    repo = DataRepository(db_session)
    repo.save_data_points(validated_data)
    
    # 3. Vérification en DB
    from backend.models.sql_models import DataPointModel
    db_point = db_session.query(DataPointModel).filter_by(indicator_code="GDP").first()
    
    assert db_point is not None
    assert db_point.value == 1.2
    assert db_point.country_code == "HTI"
