from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from backend.models.sql_models import ValeurIndicateur, Indicateur, Pays
from data_ingestion.core.models import DataPoint
from data_ingestion.utils.logger import logger

class IngestionRepository:
    """Gère la persistance des données ingérées dans la base relationnelle."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def save_data_points(self, data_points: List[DataPoint]):
        """Sauvegarde une liste de DataPoints en base avec gestion des conflits (Upsert)."""
        if not data_points:
            return

        logger.info(f"Persisting {len(data_points)} data points to database...")
        
        # Mapping des caches pour éviter des requêtes répétitives
        pays_cache = {p.iso_alpha3: p.id for p in self.db.query(Pays).all()}
        ind_cache = {i.code_indicateur: i.id for i in self.db.query(Indicateur).all()}

        save_count = 0
        for dp in data_points:
            pays_id = pays_cache.get(dp.country_code)
            ind_id = ind_cache.get(dp.indicator_code)

            if not pays_id or not ind_id:
                logger.warning(f"Skipping point: Country {dp.country_code} or Indicator {dp.indicator_code} not found in DB.")
                continue

            try:
                # Préparation du dictionnaire pour SQLite
                stmt = insert(ValeurIndicateur).values(
                    indicateur_id=ind_id,
                    pays_id=pays_id,
                    date_valeur=dp.date_value,
                    valeur_numerique=dp.value,
                    statut=dp.status,
                    metadata_json={"source": dp.source_name, "raw_confidence": dp.confidence_score}
                )

                # Gestion du conflit (UPSERT) pour SQLite
                stmt = stmt.on_conflict_do_update(
                    index_elements=['indicateur_id', 'pays_id', 'date_valeur', 'statut'],
                    set_={"valeur_numerique": stmt.excluded.valeur_numerique}
                )

                self.db.execute(stmt)
                save_count += 1
            except Exception as e:
                logger.error(f"Error persisting point {dp}: {e}")
                self.db.rollback()

        self.db.commit()
        logger.info(f"Successfully persisted {save_count} records.")
