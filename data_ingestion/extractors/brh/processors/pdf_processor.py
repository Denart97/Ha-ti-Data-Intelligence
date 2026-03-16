import pdfplumber
import os
import logging
from typing import List, Tuple, Optional
import pandas as pd

logger = logging.getLogger("brh_pdf")


def extract_text_and_tables(pdf_path: str, text_out_dir: str, tables_out_dir: Optional[str] = None) -> Tuple[str, List[str]]:
    """Extracts text and tables from a PDF.
    Writes extracted text into `text_out_dir` and tables into `tables_out_dir` (falls back to text_out_dir).
    Returns path to text file and list of CSV paths for tables.
    """
    if tables_out_dir is None:
        tables_out_dir = text_out_dir
    text_out = os.path.join(text_out_dir, os.path.basename(pdf_path) + '.txt')
    table_paths: List[str] = []
    # Ensure output directories exist
    os.makedirs(text_out_dir, exist_ok=True)
    os.makedirs(tables_out_dir, exist_ok=True)

    try:
        # Open PDF and iterate pages
        with pdfplumber.open(pdf_path) as pdf:
            all_text = []
            for i, page in enumerate(pdf.pages):
                try:
                    txt = page.extract_text() or ''
                except Exception:
                    txt = ''
                all_text.append(txt)

                # Try to extract tables using pdfplumber's table extraction.
                # Each detected table is converted to a pandas DataFrame
                # and written as a CSV into the processed tables directory.
                try:
                    tables = page.extract_tables()
                    for ti, table in enumerate(tables):
                        df = pd.DataFrame(table[1:], columns=table[0]) if table and len(table) > 1 else pd.DataFrame(table)
                        table_path = os.path.join(tables_out_dir, f"{os.path.basename(pdf_path)}_p{i+1}_t{ti+1}.csv")
                        df.to_csv(table_path, index=False)
                        table_paths.append(table_path)
                except Exception as e:
                    logger.debug(f"table extraction failed page {i}: {e}")

        with open(text_out, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(all_text))
    except Exception as e:
        logger.error(f"PDF processing failed {pdf_path}: {e}")
        return ('', [])

    return (text_out, table_paths)
