from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.schemas.api_schemas import ChatRequest, ChatResponse
from backend.services.ai.orchestrator import HybridOrchestrator
from backend.services.ai.briefing import BriefingService
from backend.db.pg_session import get_db
import uuid

ai_router = APIRouter(prefix="/ai", tags=["AI & Chat"])
orchestrator = HybridOrchestrator()

@ai_router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    from backend.core.sanitizer import InputSanitizer
    from backend.core.exceptions import PromptInjectionError
    
    try:
        # 1. Sanitisation des entrées
        safe_query = InputSanitizer.sanitize_query(request.query)
        
        # 2. Traitement Orchestrateur
        result = orchestrator.handle_query(safe_query)
        
        return ChatResponse(
            query=result["query"],
            intent=result["intent"],
            answer=result["answer"],
            sources=result["sources"],
            request_id=str(uuid.uuid4())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine error: {str(e)}")

@ai_router.get("/brief")
async def generate_briefing(profile: str, country: str = "HTI", db: Session = Depends(get_db)):
    """Génère un briefing économique profilé."""
    try:
        service = BriefingService(db)
        content = service.generate_briefing(profile, country)
        return {"profile": profile, "country": country, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Briefing generation error: {str(e)}")
