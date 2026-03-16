from typing import List
from data_ingestion.core.base import BaseExtractor
from data_ingestion.core.models import DataPoint
from .scrapers import BRHScraper
from .crawler import BRHSiteCrawler
from data_ingestion.utils.logger import logger

class BRHExtractor(BaseExtractor):
    """Implémentation de l'extracteur pour la BRH."""

    def __init__(self):
        super().__init__(name="BRH")
        self.scraper = BRHScraper()

    def fetch_data(self, requested_indicators: List[str], countries: List[str]) -> List[DataPoint]:
        """
        Pour le moment, l'implémentation se concentre sur le taux de change
        récupérable par scraping HTML.
        """
        all_data_points = []
        
        # On ne traite que Haïti pour la BRH par définition
        if "HTI" not in countries:
            logger.warning("BRH Extractor called without HTI in countries. Skipping.")
            return []

        # Taux de change
        if "USD_HTG_REF" in requested_indicators or "EUR_HTG" in requested_indicators:
            rates = self.scraper.fetch_exchange_rate()
            all_data_points.extend(rates)

        # Indicateurs dynamiques chargés via boutons/JS (inflation, réserves, bons, etc.)
        dynamic_requested = [i for i in requested_indicators if i not in ["USD_HTG_REF", "EUR_HTG"]]
        if dynamic_requested:
            dynamic_data = self.scraper.fetch_dynamic_indicators(dynamic_requested)
            all_data_points.extend(dynamic_data)

        return self.validate_data(all_data_points)

    def crawl_and_download_resources(self) -> None:
        """Role de crawl complet BRH pour documents/statistiques et sauvegarde locale."""
        crawler = BRHSiteCrawler(base_url=BRHSiteCrawler().base_url)
        crawler.crawl()
        crawler.export_metadata_csv('data_ingestion/extractors/brh/crawl_metadata.csv')
