import pytest
from sqlalchemy import create_mock_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.db.pg_session import get_db

# Mock DB URL pour les tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def db_session():
    """Crée une session DB isolée pour les tests."""
    # Note: Pour un vrai MVP, on utiliserait une DB temporaire ou des mocks SQLAlchemy
    from backend.models.sql_models import Base
    from sqlalchemy import create_engine
    
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def client(db_session):
    """Client de test FastAPI avec injection de la DB de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def mock_openai(mocker):
    """Fixture pour mocker les appels OpenAI."""
    mock = mocker.patch("openai.resources.chat.Completions.create")
    mock.return_value.choices[0].message.content = "Réponse simulée par le test."
    return mock
