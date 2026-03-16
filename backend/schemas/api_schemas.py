from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date

# --- SCHÉMAS AI / CHAT ---
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    stream: bool = False

class SourceMetadata(BaseModel):
    id: int
    filename: str
    page: Optional[int] = None

class ChatResponse(BaseModel):
    query: str
    intent: str
    answer: str
    sources: List[SourceMetadata]
    request_id: str

# --- SCHÉMAS DATA / ANALYTICS ---
class IndicatorTrendRequest(BaseModel):
    indicator_code: str
    country_iso: str
    period: Optional[str] = "max"

class ComparisonRequest(BaseModel):
    indicators: List[str]
    countries: List[str]
    base_100: bool = False

class DatasetStatus(BaseModel):
    indicator: str
    source: str
    last_update: Optional[date]
