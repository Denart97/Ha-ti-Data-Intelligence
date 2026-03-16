from datetime import date
from typing import List, Dict, Any
from data_ingestion.core.models import DataPoint
from data_ingestion.utils.logger import logger

class WBNormalizer:
    """Transforme les réponses JSON de la Banque Mondiale en objets DataPoint."""

    @staticmethod
    def to_data_points(raw_data: List[Any], internal_indicator_code: str) -> List[DataPoint]:
        """Convertit le format [metadata, list_data] en List[DataPoint]."""
        if not raw_data or len(raw_data) < 2:
            return []
        
        records = raw_data[1]
        data_points = []
        
        for record in records:
            try:
                # La Banque Mondiale renvoie les années en string "2023"
                # On normalise en fin d'année par défaut
                year = int(record['date'])
                norm_date = date(year, 12, 31)
                
                # Conversion du code pays (WB renvoie ISO2 dans 'countryiso3code' ou 'country.id')
                # On privilégie la version 3 lettres si présente
                iso3 = record.get('countryiso3code')
                
                dp = DataPoint(
                    indicator_code=internal_indicator_code,
                    country_code=iso3 if iso3 else "UNKNOWN",
                    value=record['value'],
                    date_value=norm_date,
                    source_name="Banque Mondiale",
                    status="FINAL"
                )
                data_points.append(dp)
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse WB record: {record}. Error: {e}")
                
        return data_points
