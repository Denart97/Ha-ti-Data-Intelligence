"""BRH ingestion helper

Utilities to read CSVs produced by the BRH extractor and persist them
into the project's analytical database. The module contains lightweight
heuristics to map CSV columns to an indicator name, value and date. It
creates or reuses `Source`, `Pays`, `Dataset` and `Indicateur` records
and inserts `ValeurIndicateur` rows while avoiding duplicates.

This file is intentionally pragmatic: it focuses on robust ingestion of
tabular outputs produced by the extractor and processors.
"""

import os
import pandas as pd
import datetime
import re
import logging

from backend.db.pg_session import SessionLocal
from backend.models.sql_models import Source, Pays, Dataset, Indicateur, ValeurIndicateur

logger = logging.getLogger('brh_ingest')


def _normalize_code(name: str) -> str:
    """Create a short, DB-safe indicator code from a human label.

    Example: "Inflation (IPC)" -> "INFLATION_IPC"
    The code is uppercased, non-alphanumeric characters are replaced
    by underscores and length is capped to 50 chars to fit DB column.
    """
    s = re.sub(r"[^0-9A-Za-z]+", '_', name.strip()).upper()
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:50]


def _parse_numeric(s: str):
    """Attempt to parse a numeric value from a string.

    The function tolerates common formats found in BRH tables: thousands
    separators (commas and spaces), non-breaking spaces and percent
    signs. Returns a float or None.
    """
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    try:
        s = str(s)
        s = s.replace('\xa0', ' ')
        # remove percent sign but keep note
        s = s.replace('%', '')
        # remove thousands separators and spaces
        s = s.replace(',', '').replace(' ', '')
        return float(re.findall(r"-?\d+\.?\d*", s)[0])
    except Exception:
        return None


def ingest_csv_list(csv_paths, source_name='BRH', country_iso='HTI', dataset_code='BRH_CRAWL'):
    db = SessionLocal()
    try:
        # ensure source
        src = db.query(Source).filter(Source.nom == source_name).first()
        if not src:
            src = Source(nom=source_name, site_web='https://www.brh.ht')
            db.add(src)
            db.flush()

        # ensure country
        country = db.query(Pays).filter(Pays.iso_alpha3 == country_iso).first()
        if not country:
            country = Pays(iso_alpha3=country_iso, nom_fr=country_iso)
            db.add(country)
            db.flush()

        # dataset
        ds = db.query(Dataset).filter(Dataset.source_id == src.id, Dataset.code_dataset == dataset_code).first()
        if not ds:
            ds = Dataset(source_id=src.id, code_dataset=dataset_code, url_origine='https://www.brh.ht')
            db.add(ds)
            db.flush()

        inserted = 0
        for csv_path in csv_paths:
            if not os.path.exists(csv_path):
                logger.warning('CSV not found: %s', csv_path)
                continue
            try:
                df = pd.read_csv(csv_path)
            except Exception:
                try:
                    df = pd.read_csv(csv_path, encoding='latin-1')
                except Exception:
                    logger.exception('Failed to read CSV %s', csv_path)
                    continue

            # heuristics: look for indicator/name column and value column
            cols = [c.lower() for c in df.columns]
            name_col = None
            value_col = None
            date_col = None
            for c in df.columns:
                lc = c.lower()
                if any(k in lc for k in ['indicateur', 'indicator', 'nom', 'name', 'label']):
                    name_col = c
                if any(k in lc for k in ['valeur', 'value', 'val', 'montant']):
                    value_col = c
                if any(k in lc for k in ['date', 'period', 'periode', 'annee', 'year']):
                    date_col = c

            if name_col is None and df.shape[1] >= 2:
                name_col = df.columns[0]
            if value_col is None and df.shape[1] >= 2:
                value_col = df.columns[1]

            for _, row in df.iterrows():
                name = str(row.get(name_col)) if name_col else None
                raw_val = row.get(value_col) if value_col else None
                numeric = _parse_numeric(raw_val)

                if date_col:
                    try:
                        date_val = pd.to_datetime(row.get(date_col)).date()
                    except Exception:
                        date_val = datetime.date.today()
                else:
                    date_val = datetime.date.today()

                if not name or numeric is None:
                    continue

                code = _normalize_code(name)
                ind = db.query(Indicateur).filter(Indicateur.code_indicateur == code).first()
                if not ind:
                    ind = Indicateur(code_indicateur=code, nom=name)
                    db.add(ind)
                    db.flush()

                # check existing value
                existing = db.query(ValeurIndicateur).filter(
                    ValeurIndicateur.indicateur_id == ind.id,
                    ValeurIndicateur.pays_id == country.id,
                    ValeurIndicateur.date_valeur == date_val
                ).first()

                if existing:
                    continue

                dp = ValeurIndicateur(
                    indicateur_id=ind.id,
                    pays_id=country.id,
                    dataset_id=ds.id,
                    date_valeur=date_val,
                    valeur_numerique=numeric,
                    statut='FINAL',
                    metadata_json={'source_file': os.path.basename(csv_path)}
                )
                db.add(dp)
                inserted += 1

        db.commit()
        logger.info('Ingested %d rows from %d CSV(s)', inserted, len(csv_paths))
        return inserted
    except Exception:
        db.rollback()
        logger.exception('Ingestion failed')
        raise
    finally:
        db.close()
