from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

class DataPoint(BaseModel):
    """Modèle standardisé pour un point de donnée unique."""
    indicator_code: str = Field(..., description="Code taxonomie de l'indicateur")
    country_code: str = Field(..., description="Code ISO3 du pays (ex: HTI)")
    value: Optional[float] = Field(None, description="Valeur numérique")
    date_value: date = Field(..., description="Date du point de donnée")
    source_name: str = Field(..., description="Nom de la source d'origine")
    status: str = Field("FINAL", description="Statut de la donnée (PROVISOIRE, FINAL)")
    confidence_score: float = Field(1.0, description="Score de fiabilité de 0.0 à 1.0")

class ExtractionResult(BaseModel):
    """Modèle pour le résultat d'une session d'extraction."""
    source: str
    timestamp: date
    records_count: int
    data_points: List[DataPoint]
    status: str = "SUCCESS"
    error_message: Optional[str] = None
