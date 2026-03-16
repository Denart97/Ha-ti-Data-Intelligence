import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from requests import Response

from .models import ResourceMetadata
from .parser import detect_file_type


class DocumentDownloader:
    def __init__(self, output_dir: str = 'data_ingestion/extractors/brh/downloads', timeout: int = 30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BRH-Scraper/1.0 (https://github.com/your_org/RAG_BRH)'
        })
        self.timeout = timeout

    def _compute_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _safe_filename(self, url: str, content_type: Optional[str] = None) -> str:
        basename = os.path.basename(url.split('?')[0])
        if not basename:
            basename = 'resource'
        basename = basename.replace('/', '_').replace('?', '_')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        suffix = ''
        if content_type and 'pdf' in content_type.lower():
            suffix = '.pdf'
        if content_type and 'sheet' in content_type.lower() or basename.lower().endswith(('.xls', '.xlsx')):
            suffix = '.xlsx'
        if content_type and 'csv' in content_type.lower() or basename.lower().endswith('.csv'):
            suffix = '.csv'
        if content_type and basename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp')):
            suffix = Path(basename).suffix

        if not Path(basename).suffix and suffix:
            basename += suffix

        return f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{basename}"

    def download(self, url: str, category: str = 'unknown') -> ResourceMetadata:
        resource = ResourceMetadata(
            source_url=url,
            title=None,
            file_type='unknown',
            crawl_date=datetime.utcnow(),
            category=category,
            local_path=None,
            status='pending',
            extracted_text_path=None,
            error=None
        )

        try:
            resp = self.session.get(url, timeout=self.timeout, stream=True)
            resp.raise_for_status()

            content_type = resp.headers.get('Content-Type', '')
            resource.file_type = detect_file_type(url, content_type)

            content = resp.content
            sha = self._compute_hash(content)

            local_name = self._safe_filename(url, content_type)
            file_path = self.output_dir / local_name

            # Prévenir les doublons via hash
            if file_path.exists():
                with file_path.open('rb') as f:
                    existing_hash = self._compute_hash(f.read())
                if existing_hash == sha:
                    resource.status = 'skipped'
                    resource.local_path = str(file_path)
                    return resource

            with file_path.open('wb') as f:
                f.write(content)

            resource.local_path = str(file_path)
            resource.status = 'downloaded'

        except Exception as e:
            resource.status = 'failed'
            resource.error = str(e)

        return resource
