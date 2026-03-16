import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from data_ingestion.utils.logger import logger

class WBClient:
    """Client pour interagir avec l'API v2 de la Banque Mondiale."""
    
    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
    def get_indicator_data(self, country_code: str, indicator_code: str, date_range: str = "2000:2024"):
        """Récupère les données d'un indicateur pour un pays donné."""
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {
            "format": "json",
            "date": date_range,
            "per_page": 1000
        }
        
        logger.debug(f"Calling WB API: {url} with params {params}")
        response = self.session.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"WB API error {response.status_code}: {response.text}")
            response.raise_for_status()
            
        return response.json()
