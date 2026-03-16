from datetime import date
from typing import List, Dict, Any, Union
from data_ingestion.core.models import DataPoint
from data_ingestion.utils.logger import logger

class IMFParser:
    """Parseur pour le format SDMX-JSON du FMI."""

    @staticmethod
    def parse_obs(obs: Union[Dict, List]) -> List[Dict]:
        """Normalise les observations en une liste de dicts."""
        if isinstance(obs, dict):
            return [obs]
        return obs if isinstance(obs, list) else []

    def to_data_points(self, raw_json: Dict[str, Any], taxi_code: str, iso3_code: str) -> List[DataPoint]:
        """Extrait les points de données du JSON SDMX."""
        if not raw_json or 'CompactData' not in raw_json:
            return []

        dataset = raw_json['CompactData'].get('DataSet', {})
        series = dataset.get('Series', {})
        
        # Le FMI peut renvoyer un objet unique ou une liste
        series_list = series if isinstance(series, list) else [series]
        data_points = []
        
        for s in series_list:
            observations = self.parse_obs(s.get('Obs', []))
            
            # Gestion du multiplicateur d'unité (UNIT_MULT)
            # ex: Si UNIT_MULT="6", multiplier par 10^6
            unit_mult = int(s.get('@UNIT_MULT', 0))
            multiplier = 10 ** unit_mult

            for obs in observations:
                try:
                    raw_val = obs.get('@OBS_VALUE')
                    if raw_val is None: continue
                    
                    val = float(raw_val) * multiplier
                    period = obs.get('@TIME_PERIOD')
                    
                    # Normalisation date (YYYY or YYYY-MXX)
                    if '-' in period: # Mensuel ou Trimestriel ex: 2023-M03
                        y, m = period.split('-')
                        # Simplification : fin du mois approximatif
                        norm_date = date(int(y), int(m[1:]), 28)
                    else:
                        norm_date = date(int(period), 12, 31)

                    dp = DataPoint(
                        indicator_code=taxi_code,
                        country_code=iso3_code,
                        value=val,
                        date_value=norm_date,
                        source_name="FMI",
                        status="FINAL"
                    )
                    data_points.append(dp)
                except Exception as e:
                    logger.warning(f"Failed to parse IMF obs: {obs}. Error: {e}")

        return data_points
