from unittest.mock import MagicMock, patch
from backend.api.main import app
from backend.services.ai.orchestrator import HybridOrchestrator

client = TestClient(app)

@patch('backend.services.rag.retriever.OpenAI')
@patch('backend.services.ai.responder.OpenAI')
@patch('backend.services.sql.agent.OpenAI')
def test_hybrid_orchestrator_seeding(mock_sql_openai, mock_resp_openai, mock_rag_openai):
    """Vérifie que l'orchestrateur trouve les données injectées par le seeding."""
    
    # Mock Embeddings
    mock_rag_openai.return_value.embeddings.create.return_value.data = [MagicMock(embedding=[0.1]*1536)]
    
    # Mock SQL Translation
    mock_sql_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="SELECT * FROM pays;"))
    ]
    
    # Mock Final Response
    mock_resp_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Réponse simulée pour test intégré."))
    ]

    orchestrator = HybridOrchestrator()
    """Vérifie que l'orchestrateur trouve les données injectées par le seeding."""
    orchestrator = HybridOrchestrator()
    
    # Test d'une question hybride (SQL + RAG)
    query = "Quelle est l'inflation en Haïti et que dit la BRH sur les prix ?"
    result = orchestrator.handle_query(query)
    
    # Vérifications
    assert result["intent"] in ["HYBRID", "RAG", "SQL"]
    assert "answer" in result
    assert len(result["answer"]) > 50
    # On vérifie que les sources documentaires sont présentes (venant du deep seed)
    assert len(result["sources"]) > 0 
    assert any("BRH" in s["filename"] for s in result["sources"])

def test_api_ask_endpoint():
    """Vérifie l'endpoint /ai/ask de bout en bout."""
    response = client.post("/ai/ask", json={"query": "Taux de change actuel ?"})
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "request_id" in data

def test_database_not_empty():
    """Vérifie que la base de données contient le minimum vital."""
    from backend.db.pg_session import SessionLocal
    from backend.models.sql_models import ValeurIndicateur, Pays
    
    db = SessionLocal()
    try:
        val_count = db.query(ValeurIndicateur).count()
        pays_count = db.query(Pays).count()
        
        assert pays_count >= 1
        assert val_count >= 100 # On attend le cumul WB + Seed
    finally:
        db.close()
