from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import date

class TimeSeriesPoint(BaseModel):
    """Un point unique dans une série temporelle."""
    date: date
    value: float
    status: str = "FINAL"

class AggregateStats(BaseModel):
    """Statistiques calculées sur une série."""
    min_value: float
    max_value: float
    mean_value: float
    median_value: Optional[float] = None
    variation_yoy: Optional[float] = Field(None, description="Variation Year-over-Year en %")
    variation_mom: Optional[float] = Field(None, description="Variation Month-over-Month en %")
    trend: str = Field(..., description="UP, DOWN, STABLE")

class CountryComparison(BaseModel):
    """Comparaison d'un indicateur entre plusieurs pays."""
    indicator_code: str
    unit: str
    data: Dict[str, List[TimeSeriesPoint]] # Key: ISO_ALPHA3, Value: Series
    summary: str

class AnalyticalBrief(BaseModel):
    """Briefing analytique prêt pour l'IA ou l'utilisateur."""
    indicator_name: str
    period: str
    main_stats: AggregateStats
    observation: str
    data_points: List[TimeSeriesPoint]
