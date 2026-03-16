from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ResourceMetadata:
    source_url: str
    title: Optional[str]
    file_type: str  # html, pdf, xls, xlsx, csv, image, other
    crawl_date: datetime
    category: Optional[str]
    local_path: Optional[str]
    status: str  # pending, downloaded, skipped, failed, extracted
    extracted_text_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CrawlTask:
    url: str
    depth: int
    priority: int
