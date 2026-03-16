import re
from datetime import datetime
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

DATA_KEYWORDS_HIGH = ["statistiques", "publication", "bulletin", "rapport", "vbulletin", "données", "tableau", "série"]
DATA_KEYWORDS_MEDIUM = ["page", "institutionnel", "mission", "service"]
DATA_KEYWORDS_LOW = ["contact", "plan", "avis", "actualite"]


def normalize_url(url: str) -> str:
    return url.strip().split('#')[0].strip()


def is_internal(url: str, domain: str) -> bool:
    return url.startswith(domain) or (url.startswith('/') and not url.startswith('//'))


def detect_file_type(url: str, content_type: Optional[str] = None) -> str:
    if content_type:
        lower = content_type.lower()
        if 'pdf' in lower:
            return 'pdf'
        if 'excel' in lower or 'spreadsheet' in lower or 'sheet' in lower:
            return 'xls'
        if 'csv' in lower:
            return 'csv'
        if 'image' in lower:
            return 'image'

    u = url.lower()
    if u.endswith('.pdf'):
        return 'pdf'
    if u.endswith('.xlsx') or u.endswith('.xls'):
        return 'xls'
    if u.endswith('.csv'):
        return 'csv'
    if re.search(r'\.(png|jpe?g|gif|svg|bmp|tiff)$', u):
        return 'image'
    return 'html'


def classify_page(url: str, title: Optional[str] = None) -> str:
    text = ' '.join(filter(None, [url.lower(), (title or '').lower()]))
    score = 0
    for kw in DATA_KEYWORDS_HIGH:
        if kw in text:
            score += 10
    for kw in DATA_KEYWORDS_MEDIUM:
        if kw in text:
            score += 5
    for kw in DATA_KEYWORDS_LOW:
        if kw in text:
            score += 1

    if score >= 15:
        return 'high'
    if score >= 6:
        return 'medium'
    return 'low'


def extract_links(html: str, base_url: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    links = []

    for tag in soup.find_all(['a', 'link', 'area', 'button', 'script']):
        if tag.name == 'a' and tag.get('href'):
            links.append((tag.get('href').strip(), tag.get_text(strip=True)))
        elif tag.get('href'):
            links.append((tag.get('href').strip(), ''))
        elif tag.get('src'):
            links.append((tag.get('src').strip(), ''))

    # On peut ajouter un parser JS minimal pour data-url ou onclick
    for tag in soup.find_all(True):
        data_url = tag.get('data-url') or tag.get('data-href')
        if data_url:
            links.append((data_url.strip(), ''))

    return links


def extract_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    if title:
        return title
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    return None
