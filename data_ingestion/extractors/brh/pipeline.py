"""BRH Pipeline orchestrator

This module coordinates navigation (Playwright), discovery of resources,
downloading and extraction. It writes raw files and processed CSVs and
optionally calls the ingestion helper to persist discovered data.
"""

import logging
from typing import List, Dict
from datetime import datetime
from urllib.parse import urljoin

from .playwright_navigator import PlaywrightNavigator
from .downloader import DocumentDownloader
from .processors.html_table_extractor import extract_tables_from_html
from .processors.pdf_processor import extract_text_and_tables
from .utils.io import ensure_dirs
from .models import ResourceMetadata
from .ingest import ingest_csv_list

logger = logging.getLogger('brh_pipeline')


class BRHPipeline:
    def __init__(self, base_url: str = 'https://www.brh.ht'):
        self.base_url = base_url
        self.paths = ensure_dirs('data')
        self.downloader = DocumentDownloader(output_dir=self.paths['raw_pdf'])

    def run_navigation_and_extract(self, main_menu: str, sub_menu: str):
                """Navigate BRH menus and extract resources.

                - `main_menu` and `sub_menu` are the visible labels in the BRH menu.
                - The method returns a list of ResourceMetadata describing each
                    resource discovered or downloaded.
                """

                results = []
        with PlaywrightNavigator(base_url=self.base_url, headless=True) as nav:
            nav.open_home()
            html = nav.navigate_menu(main_menu, sub_menu)
            # store intermediate page
            # collect links
            links = nav.collect_links_from_current_page()

            for link in links:
                href = link.get('href')
                if not href:
                    continue
                # normalize
                if href.startswith('/'):
                    href = urljoin(self.base_url, href)
                if href.startswith('#'):
                    continue

                resource = ResourceMetadata(
                    source_url=href,
                    title=link.get('text') or None,
                    file_type='unknown',
                    crawl_date=datetime.utcnow(),
                    category=sub_menu,
                    local_path=None,
                    status='pending'
                )

                # classify by extension and handle accordingly
                lower = href.lower()
                try:
                    if lower.endswith('.pdf'):
                        # download pdf
                        md = self.downloader.download(href, category=sub_menu)
                        if md.status == 'downloaded' and md.local_path:
                            txt_path, table_paths = extract_text_and_tables(md.local_path, self.paths['processed_text'], self.paths['processed_tables'])
                            md.extracted_text_path = txt_path
                            # ingest any tables extracted from PDF
                            try:
                                if table_paths:
                                    ingest_csv_list(table_paths, source_name='BRH', country_iso='HTI')
                            except Exception:
                                logger.exception('Ingestion failed for PDF tables')
                        resource = md
                    elif lower.endswith(('.xls', '.xlsx')):
                        md = self.downloader.download(href, category=sub_menu)
                        resource = md
                        # parse excel and write CSVs into processed tables, then ingest
                        try:
                            if md.status == 'downloaded' and md.local_path:
                                from .processors.excel_processor import read_excel_or_csv
                                csvs = read_excel_or_csv(md.local_path, self.paths['processed_tables'])
                                if csvs:
                                    ingest_csv_list(csvs, source_name='BRH', country_iso='HTI')
                        except Exception:
                            logger.exception('Excel processing failed')
                    elif lower.endswith('.csv'):
                        md = self.downloader.download(href, category=sub_menu)
                        resource = md
                        # ingest csv directly
                        try:
                            if md.status == 'downloaded' and md.local_path:
                                ingest_csv_list([md.local_path], source_name='BRH', country_iso='HTI')
                        except Exception:
                            logger.exception('CSV ingestion failed')
                    else:
                        # treat as HTML -- fetch via Playwright to allow JS
                        html_content = nav.fetch_html(href)
                        # save raw html
                        import os
                        fname = os.path.join(self.paths['raw_html'], href.split('/')[-1] or 'index.html')
                        with open(fname, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        resource.local_path = fname
                        resource.file_type = 'html'
                        # extract tables
                        tables = extract_tables_from_html(html_content, self.paths['processed_tables'])
                        resource.status = 'downloaded'
                        # ingest any extracted tables into DB
                        try:
                            if tables:
                                ingest_csv_list(tables, source_name='BRH', country_iso='HTI')
                        except Exception:
                            logger.exception('Ingestion failed for HTML tables')
                except Exception as e:
                    resource.status = 'failed'
                    resource.error = str(e)

                results.append(resource)

        # save metadata CSV
        import csv
        meta_file = self.paths['metadata'] + '/resources.csv'
        with open(meta_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['source_url', 'title', 'file_type', 'crawl_date', 'category', 'local_path', 'status', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({
                    'source_url': r.source_url,
                    'title': r.title,
                    'file_type': r.file_type,
                    'crawl_date': r.crawl_date,
                    'category': r.category,
                    'local_path': r.local_path,
                    'status': r.status,
                    'error': r.error
                })

        logger.info(f"Pipeline finished: {len(results)} resources processed")
        return results
