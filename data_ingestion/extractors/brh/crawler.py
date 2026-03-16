import json
import logging
import os
import queue
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from requests import exceptions

from .downloader import DocumentDownloader
from .models import CrawlTask, ResourceMetadata
from .parser import (
    classify_page,
    detect_file_type,
    extract_links,
    extract_title,
    is_internal,
    normalize_url,
)


logger = logging.getLogger('brh_crawler')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logger.addHandler(handler)


class BRHSiteCrawler:
    def __init__(
        self,
        base_url: str = 'https://www.brh.ht',
        max_depth: int = 4,
        max_pages: int = 500,
        output_dir: str = 'data_ingestion/extractors/brh/downloads',
        metadata_path: str = 'data_ingestion/extractors/brh/crawl_metadata.json',
    ):
        self.base_url = base_url.rstrip('/')
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.task_counter = 0
        self.resource_metadata: List[ResourceMetadata] = []
        self.downloader = DocumentDownloader(output_dir=output_dir)
        self.metadata_path = metadata_path

    def _push_task(self, url: str, depth: int, priority: int):
        u = normalize_url(url)
        if u in self.visited:
            return
        if depth > self.max_depth:
            return
        self.task_counter += 1
        self.task_queue.put((priority, self.task_counter, CrawlTask(url=u, depth=depth, priority=priority)))
        logger.debug(f"Queue add: {u} (depth {depth} / prio {priority})")

    def _get_priority(self, url: str, title: Optional[str]) -> int:
        category = classify_page(url, title)
        if category == 'high':
            return 1
        if category == 'medium':
            return 5
        return 10

    def _save_metadata(self):
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump([r.__dict__ for r in self.resource_metadata], f, default=str, indent=2, ensure_ascii=False)
            logger.info(f"Metadata saved to {self.metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def crawl(self, start_url: Optional[str] = None):
        if not start_url:
            start_url = self.base_url

        self._push_task(start_url, depth=0, priority=1)

        while not self.task_queue.empty() and len(self.visited) < self.max_pages:
            _, _, task = self.task_queue.get()
            url = task.url

            if url in self.visited:
                continue

            self.visited.add(url)
            logger.info(f"Crawling ({len(self.visited)}/{self.max_pages}): {url}")

            try:
                resp = self.downloader.session.get(url, timeout=20)
                resp.raise_for_status()
            except exceptions.RequestException as e:
                logger.warning(f"Request failed {url}: {e}")
                continue

            content_type = resp.headers.get('Content-Type', '')
            detected_type = detect_file_type(url, content_type)

            # Document links
            if detected_type != 'html':
                md = self.downloader.download(url, category='document')
                self.resource_metadata.append(md)
                self._save_metadata()
                continue

            # Page HTML
            html = resp.text
            title = extract_title(html)
            page_category = classify_page(url, title)
            logger.info(f"Page type {page_category} title {title}")

            # Enregistrer la page en tant que ressource si prioritaire/données
            if page_category in ['high', 'medium']:
                self.resource_metadata.append(ResourceMetadata(
                    source_url=url,
                    title=title,
                    file_type='html',
                    crawl_date=datetime.utcnow(),
                    category=page_category,
                    local_path=None,
                    status='crawled'
                ))

            # Extraire liens
            links = extract_links(html, url)

            for raw_link, _label in links:
                normalized = normalize_url(raw_link)
                if not normalized:
                    continue

                if normalized.startswith('//'):
                    normalized = 'https:' + normalized
                if normalized.startswith('/'):
                    normalized = self.base_url + normalized

                if normalized.startswith('http') and self.base_url not in normalized:
                    # externe : télécharger si document (PDF, xls, csv).
                    ftype = detect_file_type(normalized)
                    if ftype in ('pdf', 'xls', 'csv', 'image'):
                        md = self.downloader.download(normalized, category='external_doc')
                        self.resource_metadata.append(md)
                    continue

                if normalized.startswith(self.base_url):
                    priority = self._get_priority(normalized, None)
                    self._push_task(normalized, depth=task.depth + 1, priority=priority)

            self._save_metadata()
            time.sleep(0.8)

        logger.info(f"Crawl fini : {len(self.visited)} pages visitées")
        self._save_metadata()

    def export_metadata_csv(self, csv_path: str):
        import csv

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['source_url', 'title', 'file_type', 'crawl_date', 'category', 'local_path', 'status', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for md in self.resource_metadata:
                writer.writerow({
                    'source_url': md.source_url,
                    'title': md.title,
                    'file_type': md.file_type,
                    'crawl_date': md.crawl_date,
                    'category': md.category,
                    'local_path': md.local_path,
                    'status': md.status,
                    'error': md.error,
                })

        logger.info(f"Metadata exported CSV: {csv_path}")
