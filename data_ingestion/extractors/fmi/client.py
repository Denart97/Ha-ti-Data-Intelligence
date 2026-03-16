import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from data_ingestion.utils.logger import logger

class IMFClient:
    """Client pour interagir avec les services de données du FMI (SDMX-JSON)."""
    
    BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

    def __init__(self):
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
    def fetch_compact_data(self, dataflow: str, frequency: str, country_code: str, indicator: str):
        """
        Récupère des données via l'endpoint CompactData.
        Ex: /CompactData/IFS/M.HT.FIMM_PA_NUM
        """
        # Note: Le FMI utilise souvent ISO2. On gérera le mapping dans le normalisateur.
        path = f"/CompactData/{dataflow}/{frequency}.{country_code}.{indicator}"
        url = f"{self.BASE_URL}{path}"
        
        logger.debug(f"Calling IMF API: {url}")
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"IMF data not found for {path}")
            return None
        else:
            logger.error(f"IMF API error {response.status_code}: {response.text}")
            response.raise_for_status()
