from typing import List
from data_ingestion.core.models import DataPoint
from data_ingestion.utils.logger import logger
from backend.core.audit_trail import audit_trail

class DataValidator:
    """Couche de validation finale pour garantir la qualité des données ingérées."""

    @staticmethod
    def validate(data_points: List[DataPoint]) -> List[DataPoint]:
        """Filtre les points de données invalides ou suspects."""
        valid_points = []
        
        for dp in data_points:
            # 1. Vérification des valeurs nulles
            if dp.value is None:
                audit_trail.log_data_quality_issue(dp.indicator_code, "NULL_VALUE", None, {"country": dp.country_code})
                continue

            # 2. Détection de valeurs aberrantes (Outliers bruts)
            # Ex: Une inflation à 1 000 000 % ou un PIB négatif (sauf croissance)
            if "GROWTH" not in dp.indicator_code and dp.value < 0:
                 audit_trail.log_data_quality_issue(dp.indicator_code, "SUSPECT_NEGATIVE", dp.value, {"country": dp.country_code})
                 logger.warning(f"Suspect negative value for non-growth indicator: {dp}")
            
            if abs(dp.value) > 1e15: # Valeur démesurée
                audit_trail.log_data_quality_issue(dp.indicator_code, "EXTREME_OUTLIER", dp.value, {"country": dp.country_code})
                logger.error(f"Extreme outlier rejected: {dp}")
                continue

            # 3. Vérification des codes pays (Format ISO3)
            if len(dp.country_code) != 3:
                logger.warning(f"Invalid country code format: {dp.country_code}")
                continue

            valid_points.append(dp)
            
        return valid_points
