from abc import ABC, abstractmethod
from typing import List
from .models import DataPoint

class BaseExtractor(ABC):
    """Classe de base abstraite pour tous les extracteurs de sources."""
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_data(self, indicators: List[str], countries: List[str]) -> List[DataPoint]:
        """Méthode à implémenter pour récupérer les données de la source."""
        pass

    def validate_data(self, data: List[DataPoint]) -> List[DataPoint]:
        """Logique de validation commune (optionnelle)."""
        # Filtrage des valeurs absurdes ou aberrantes si nécessaire
        return [d for d in data if d.value is not None]
