import os
from pathlib import Path


def ensure_dirs(base: str = 'data') -> dict:
    basep = Path(base)
    raw = basep / 'raw'
    processed = basep / 'processed'
    metadata = basep / 'metadata'
    logs = Path('logs')

    paths = {
        'base': str(basep),
        'raw_html': str(raw / 'html'),
        'raw_pdf': str(raw / 'pdf'),
        'raw_excel': str(raw / 'excel'),
        'raw_csv': str(raw / 'csv'),
        'processed_tables': str(processed / 'tables'),
        'processed_text': str(processed / 'text'),
        'processed_json': str(processed / 'json'),
        'metadata': str(metadata),
        'logs': str(logs)
    }

    for p in paths.values():
        os.makedirs(p, exist_ok=True)

    return paths
