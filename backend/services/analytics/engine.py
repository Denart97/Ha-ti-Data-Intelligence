import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict
from backend.models.sql_models import ValeurIndicateur, Indicateur, Pays
from backend.services.analytics.schemas import TimeSeriesPoint, AggregateStats, CountryComparison
from data_ingestion.utils.logger import logger

class AnalyticsEngine:
    """Moteur de calcul statistique et analytique sur les données macroéconomiques."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_time_series(self, indicator_code: str, country_iso: str) -> List[TimeSeriesPoint]:
        """Récupère une série temporelle brute ordonnée depuis la DB."""
        results = (
            self.db.query(ValeurIndicateur)
            .join(Indicateur).join(Pays)
            .filter(and_(
                Indicateur.code_indicateur == indicator_code,
                Pays.iso_alpha3 == country_iso
            ))
            .order_by(ValeurIndicateur.date_valeur.asc())
            .all()
        )
        return [TimeSeriesPoint(date=r.date_valeur, value=r.valeur_numerique, status=r.statut) for r in results]

    def calculate_stats(self, series: List[TimeSeriesPoint]) -> Optional[AggregateStats]:
        """Calcule les statistiques descriptives et les tendances sur une série."""
        if not series or len(series) == 0:
            return None

        # On isole proprement les valeurs valides
        values = []
        for s in series:
            try:
                v = float(s.value)
                if not np.isnan(v):
                    values.append(v)
            except (ValueError, TypeError):
                continue
                
        if len(values) == 0:
            return None

        # Utilisation de Numpy basic (ultra robuste vs Pandas sur DB sqlite small)
        v_arr = np.array(values)

        # Calcul des variations
        var_yoy = None
        if len(v_arr) >= 2:
            last_val = v_arr[-1]
            prev_val = v_arr[-2]
            if prev_val != 0:
                var_yoy = ((last_val - prev_val) / abs(prev_val)) * 100

        # Tendance
        trend = "STABLE"
        if len(v_arr) >= 3:
            recent_slope = np.polyfit(range(3), v_arr[-3:], 1)[0]
            if recent_slope > 0.05: trend = "UP"
            elif recent_slope < -0.05: trend = "DOWN"

        return AggregateStats(
            min_value=float(np.min(v_arr)),
            max_value=float(np.max(v_arr)),
            mean_value=float(np.mean(v_arr)),
            median_value=float(np.median(v_arr)),
            variation_yoy=round(float(var_yoy), 2) if var_yoy is not None else None,
            trend=trend
        )

    def compare_countries(self, indicator_code: str, countries_iso: List[str]) -> CountryComparison:
        """Produit une comparaison multi-pays pour un indicateur donné."""
        logger.info(f"Comparing countries {countries_iso} for indicator {indicator_code}")
        
        comparison_data = {}
        for iso in countries_iso:
            series = self.get_time_series(indicator_code, iso)
            comparison_data[iso] = series

        # Récupération de l'unité (via le premier indicateur trouvé)
        indicator = self.db.query(Indicateur).filter(Indicateur.code_indicateur == indicator_code).first()
        unit = indicator.unite_mesure if indicator else "N/A"

        return CountryComparison(
            indicator_code=indicator_code,
            unit=unit,
            data=comparison_data,
            summary=f"Comparaison de {indicator_code} sur {len(countries_iso)} pays."
        )

    def generate_quantitative_summary(self, indicator_code: str, country_iso: str) -> str:
        """Génère un résumé textuel des chiffres pour consommation par le LLM."""
        series = self.get_time_series(indicator_code, country_iso)
        stats = self.calculate_stats(series)
        
        if not stats:
            return f"Aucune donnée disponible pour {indicator_code} ({country_iso})."

        summary = (
            f"Analyse de {indicator_code} pour {country_iso} : "
            f"Dernière valeur : {series[-1].value}. "
            f"Variation : {stats.variation_yoy}% (YoY). "
            f"Tendance : {stats.trend}. "
            f"Moyenne historique : {round(stats.mean_value, 2)}. "
            f"Plage : [{stats.min_value} - {stats.max_value}]."
        )
        return summary
