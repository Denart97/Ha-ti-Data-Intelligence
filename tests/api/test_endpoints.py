import pytest

def test_health_check_full(client):
    """Vérifie l'endpoint de monitoring global."""
    response = client.get("/monitoring/health/full")
    assert response.status_code == 200
    data = response.json()
    assert "api" in data
    assert data["api"] == "online"

def test_ai_ask_router_valid(client, mocker):
    """Vérifie que le chat AI répond (avec mock du moteur hybride)."""
    # Mocker l'orchestrateur pour ne pas appeler OpenAI réellement
    mocker.patch(
        "backend.services.ai.orchestrator.HybridOrchestrator.handle_query",
        return_value={
            "query": "test query",
            "intent": "RAG",
            "answer": "Test answer",
            "sources": []
        }
    )
    
    response = client.post("/ai/ask", json={"query": "Quelle est la situation ?"})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "Test answer"
