from typing import List, Dict
from data_ingestion.core.base import BaseExtractor
from data_ingestion.core.models import DataPoint
from .client import WBClient
from .normalizer import WBNormalizer
from data_ingestion.utils.logger import logger

class WBExtractor(BaseExtractor):
    """Implémentation de l'extracteur pour la Banque Mondiale."""

    def __init__(self):
        super().__init__(name="Banque Mondiale")
        self.client = WBClient()
        self.normalizer = WBNormalizer()

    def fetch_data(self, indicators_map: Dict[str, str], countries: List[str]) -> List[DataPoint]:
        """
         indicators_map: Dict[Code_Taxonomie, Code_API_WB]
         countries: List[ISO3_Codes]
        """
        all_data_points = []
        
        # L'API WB permet de grouper les pays par point-virgule
        countries_str = ";".join(countries)
        
        for taxi_code, api_code in indicators_map.items():
            logger.info(f"Fetching WB data for {taxi_code} ({api_code})")
            try:
                raw_json = self.client.get_indicator_data(countries_str, api_code)
                new_points = self.normalizer.to_data_points(raw_json, taxi_code)
                all_data_points.extend(new_points)
            except Exception as e:
                logger.error(f"Failed to fetch WB indicator {taxi_code}: {e}")
                
        return self.validate_data(all_data_points)
