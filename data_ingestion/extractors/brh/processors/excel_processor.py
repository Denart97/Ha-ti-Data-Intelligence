import pandas as pd
import os
import logging
from typing import List

logger = logging.getLogger('brh_excel')


def read_excel_or_csv(path: str, out_dir: str) -> List[str]:
        """Reads an Excel or CSV file and writes sheet CSVs into `out_dir`.

        Heuristics:
        - For CSV inputs the file is copied/converted into `out_dir`.
        - For Excel files each sheet becomes a separate CSV named
            `<workbook>_<sheet>.csv`.

        Returns the list of generated CSV file paths.
        """
    out = []
    try:
        os.makedirs(out_dir, exist_ok=True)
        if path.lower().endswith('.csv'):
            df = pd.read_csv(path)
            out_path = os.path.join(out_dir, os.path.basename(path))
            df.to_csv(out_path, index=False)
            out.append(out_path)
            return out

        xl = pd.ExcelFile(path)
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            safe = f"{os.path.basename(path)}_{sheet}.csv".replace(' ', '_')
            out_path = os.path.join(out_dir, safe)
            df.to_csv(out_path, index=False)
            out.append(out_path)
    except Exception as e:
        logger.error(f"Failed to read excel/csv {path}: {e}")
    return out
