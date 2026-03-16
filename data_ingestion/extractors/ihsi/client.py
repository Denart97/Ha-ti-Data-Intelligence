import requests
from bs4 import BeautifulSoup
from data_ingestion.utils.logger import logger

class IHSIClient:
    """Client pour explorer et télécharger les données de l'IHSI."""
    
    BASE_URL = "http://www.ihsi.ht"

    def __init__(self):
        self.session = requests.Session()

    def get_latest_cpi_link(self) -> str:
        """Cherche le lien vers le dernier bulletin de l'Indice des Prix (IPC)."""
        logger.info("Checking IHSI for latest CPI bulletins...")
        try:
            # Page des rubriques économiques
            url = f"{self.BASE_URL}/pages/économie/indice-des-prix.aspx"
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Recherche du premier lien PDF dans la liste des publications
            links = soup.find_all('a', href=True)
            for link in links:
                if '.pdf' in link['href'].lower() and 'ipc' in link['href'].lower():
                    return self.BASE_URL + link['href'] if not link['href'].startswith('http') else link['href']
            
            return None
        except Exception as e:
            logger.error(f"IHSI Connection error: {e}")
            return None
