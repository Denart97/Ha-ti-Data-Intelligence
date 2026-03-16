from datetime import date
from data_ingestion.utils.logger import logger
from data_ingestion.extractors.wb.extractor import WBExtractor
from data_ingestion.extractors.fmi.extractor import IMFExtractor
from data_ingestion.extractors.brh.extractor import BRHExtractor
from data_ingestion.extractors.ihsi.extractor import IHSIExtractor
from data_ingestion.core.persistence import IngestionRepository
from data_ingestion.core.validator import DataValidator
from backend.db.pg_session import SessionLocal

# Configuration des indicateurs par source
wb_config = {
    "GDP": "NY.GDP.MKTP.KD.ZG",
    "INFLATION": "FP.CPI.TOTL.ZG",
    "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",
    "FDI": "BX.KLT.DINV.WD.GD.ZS",
    "EDUCATION_EXP": "SE.XPD.TOTL.GD.ZS",
    "HEALTH_EXP": "SH.XPD.CHEX.GD.ZS",
    "POPULATION": "SP.POP.TOTL",
    "EXTERNAL_DEBT": "DT.DOD.DECT.CD"
}

imf_config = [
    {
        "taxi_code": "INFLATION",
        "dataflow": "IFS",
        "indicator": "PCPI_PCH_PT",
        "freq": "M"
    }
]

def main():
    logger.info("Starting Multi-Source Extraction & Ingestion Job - Haiti Data Intelligence")
    
    # 1. Configuration des cibles
    countries = ["HTI", "DOM", "CUB", "JAM"] 
    
    # 2. Initialisation des composants
    db = SessionLocal()
    repository = IngestionRepository(db)
    
    wb = WBExtractor()
    imf = IMFExtractor()
    brh = BRHExtractor()
    ihsi = IHSIExtractor()

    try:
        # 3. Collecte Banque Mondiale
        wb_results = wb.fetch_data(wb_config, countries)
        wb_valid = DataValidator.validate(wb_results)
        repository.save_data_points(wb_valid)

        # 4. Collecte FMI (IMF)
        imf_results = imf.fetch_data(imf_config, countries)
        imf_valid = DataValidator.validate(imf_results)
        repository.save_data_points(imf_valid)

        # 5. Collecte BRH (Haïti uniquement)
        brh_config = [
            "USD_HTG_REF",
            "EUR_HTG",
            "CPI_HTI",
            "RESERVES_HTI",
            "M3_HTI",
            "BONS_BRH",
            "BALANCE_PAIEMENTS",
            "DEFICIT_BUDGET"
        ]
        brh_results = brh.fetch_data(brh_config, ["HTI"])
        brh_valid = DataValidator.validate(brh_results)
        repository.save_data_points(brh_valid)

        # 6. Collecte IHSI (Haïti uniquement)
        ihsi_results = ihsi.fetch_data(["CPI_GA"], ["HTI"])
        # Pas de points directs ici pour le moment (scanning PDF)

        total_records = len(wb_results) + len(imf_results) + len(brh_results)
        logger.info(f"Ingestion Job Complete. Total Records Processed: {total_records}")

    except Exception as e:
        logger.error(f"Critical error during ingestion job: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
