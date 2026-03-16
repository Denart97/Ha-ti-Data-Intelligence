from typing import List
import pandas as pd
from bs4 import BeautifulSoup
import os
import logging

logger = logging.getLogger('brh_html')


def extract_tables_from_html(html: str, out_dir: str) -> List[str]:
    """Extract HTML <table> elements into CSV files.

    - Parses the provided HTML and locates <table> elements.
    - Uses pandas.read_html to convert tables to DataFrames and writes
      CSV files into `out_dir` with names `html_table_<n>.csv`.
    - Returns list of generated CSV paths; exceptions are logged
      and extraction continues for remaining tables.
    """
    os.makedirs(out_dir, exist_ok=True)
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    csv_paths = []
    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]
            csv_file = os.path.join(out_dir, f"html_table_{i+1}.csv")
            df.to_csv(csv_file, index=False)
            csv_paths.append(csv_file)
        except Exception as e:
            logger.debug(f"Failed to parse table {i}: {e}")
    return csv_paths
