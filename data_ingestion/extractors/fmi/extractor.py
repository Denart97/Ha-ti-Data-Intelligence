from typing import List, Dict
from data_ingestion.core.base import BaseExtractor
from data_ingestion.core.models import DataPoint
from .client import IMFClient
from .parser import IMFParser
from data_ingestion.utils.logger import logger

class IMFExtractor(BaseExtractor):
    """Implémentation de l'extracteur pour le FMI."""

    # Le FMI utilise souvent les codes ISO2
    ISO3_TO_IMF = {
        "HTI": "HT",
        "DOM": "DO",
        "JAM": "JM",
        "CUB": "CU"
    }

    def __init__(self):
        super().__init__(name="FMI")
        self.client = IMFClient()
        self.parser = IMFParser()

    def fetch_data(self, config_list: List[Dict[str, str]], countries_iso3: List[str]) -> List[DataPoint]:
        """
        config_list: List de dict {
            "taxi_code": "INFLATION", 
            "dataflow": "IFS", 
            "indicator": "PCPI_PCH_PT",
            "freq": "M"
        }
        """
        all_data_points = []
        
        for iso3 in countries_iso3:
            imf_code = self.ISO3_TO_IMF.get(iso3)
            if not imf_code:
                logger.warning(f"No IMF country code mapping for {iso3}. Skipping.")
                continue

            for cfg in config_list:
                logger.info(f"Fetching IMF data for {cfg['taxi_code']} ({cfg['indicator']}) - {iso3}")
                try:
                    raw_json = self.client.fetch_compact_data(
                        dataflow=cfg['dataflow'],
                        frequency=cfg['freq'],
                        country_code=imf_code,
                        indicator=cfg['indicator']
                    )
                    
                    if raw_json:
                        new_points = self.parser.to_data_points(raw_json, cfg['taxi_code'], iso3)
                        all_data_points.extend(new_points)
                except Exception as e:
                    logger.error(f"Failed to fetch IMF indicator {cfg['taxi_code']} for {iso3}: {e}")
                    
        return self.validate_data(all_data_points)
