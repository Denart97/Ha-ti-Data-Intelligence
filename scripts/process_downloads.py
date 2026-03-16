"""Process already-downloaded BRH documents.

This helper script is intended to be run manually after a crawl has
downloaded documents into `data_ingestion/extractors/brh/downloads`.

It performs the following steps for each file:
 - PDFs: extract text and tabular regions -> write text to
   `data/processed/text` and tables to `data/processed/tables`.
 - Excel: convert each sheet to CSV into `data/processed/tables`.
 - CSV: copy into `data/processed/tables`.

After creating CSVs the script calls the ingestion helper to persist
rows into the analytical DB.
"""

from pathlib import Path
from data_ingestion.extractors.brh.utils.io import ensure_dirs
from data_ingestion.extractors.brh.processors.pdf_processor import extract_text_and_tables
from data_ingestion.extractors.brh.processors.excel_processor import read_excel_or_csv
from data_ingestion.extractors.brh.ingest import ingest_csv_list


def main():
    paths = ensure_dirs('data')
    downloads_dir = Path('data_ingestion/extractors/brh/downloads')
    proc_tables = Path(paths['processed_tables'])
    proc_text = Path(paths['processed_text'])
    created = 0

    # Iterate sorted to have deterministic processing order
    for f in sorted(downloads_dir.iterdir()):
        p = str(f)
        if p.lower().endswith('.pdf'):
            print('Processing PDF', p)
            txt, table_paths = extract_text_and_tables(p, str(proc_text), str(proc_tables))
            print('  text->', txt)
            print('  tables->', table_paths)
            if table_paths:
                ingest_csv_list(table_paths, source_name='BRH', country_iso='HTI')
            created += len(table_paths)

        elif p.lower().endswith(('.xls', '.xlsx')):
            print('Processing Excel', p)
            csvs = read_excel_or_csv(p, str(proc_tables))
            print('  csvs->', csvs)
            if csvs:
                ingest_csv_list(csvs, source_name='BRH', country_iso='HTI')
            created += len(csvs)

        elif p.lower().endswith('.csv'):
            outp = proc_tables / f.name
            try:
                import shutil
                shutil.copy(p, outp)
                ingest_csv_list([str(outp)], source_name='BRH', country_iso='HTI')
                created += 1
            except Exception as e:
                print('  copy failed', e)

    print('Done. tables created and ingested:', created)


if __name__ == '__main__':
    main()
