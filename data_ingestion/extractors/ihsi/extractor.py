from typing import List
from data_ingestion.core.base import BaseExtractor
from data_ingestion.core.models import DataPoint
from .client import IHSIClient
from data_ingestion.utils.logger import logger

class IHSIExtractor(BaseExtractor):
    """Implémentation de l'extracteur pour l'IHSI."""

    def __init__(self):
        super().__init__(name="IHSI")
        self.client = IHSIClient()

    def fetch_data(self, requested_indicators: List[str], countries: List[str]) -> List[DataPoint]:
        """
        Pour le moment, l'implémentation se concentre sur la détection 
        de nouveaux bulletins IPC.
        """
        all_data_points = []
        
        if "HTI" not in countries:
            return []

        # Exemple : Si on demande l'inflation GA (Glissement Annuel)
        if "CPI_GA" in requested_indicators:
            latest_pdf = self.client.get_latest_cpi_link()
            if latest_pdf:
                logger.info(f"New IHSI bulletin found: {latest_pdf}")
                # TODO: Dispatcher vers le module DocumentLoader pour parsing PDF avec tabula/camelot
                # Comme c'est un flux PDF, l'extraction de data structurée se fera asynchronement
            else:
                logger.warning("No new CPI bulletin found on IHSI site.")
                
        return self.validate_data(all_data_points)
