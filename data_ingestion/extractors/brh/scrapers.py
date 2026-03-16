import re
import requests
from bs4 import BeautifulSoup
from datetime import date
from typing import List, Dict, Any, Optional
from data_ingestion.core.models import DataPoint
from data_ingestion.utils.logger import logger


class BRHScraper:
    """
    Scraper complet pour le site de la Banque de la République d'Haïti (brh.ht).
    Couvre : Taux du Jour, Statistiques, Publications, Circulaires, Politique Monétaire.
    """

    BASE_URL = "https://www.brh.ht"

    # Pages avec données HTML directes
    URL_TAUX_DU_JOUR = "https://www.brh.ht/taux-du-jour/"
    URL_TAUX_REFERENCE = "https://www.brh.ht/taux-de-reference/"

    # Pages Statistiques
    URL_STATS_MONNAIE = "https://www.brh.ht/statistiques/monnaie/"
    URL_STATS_SECTEUR_REEL = "https://www.brh.ht/statistiques/secteur-reel/"
    URL_STATS_BDP = "https://www.brh.ht/statistiques/bdp-et-commerce-exterieur/"
    URL_STATS_FINANCES_PUB = "https://www.brh.ht/statistiques/finances-publiques/"

    # Politique Monétaire
    URL_TAUX_INTERET = "https://www.brh.ht/politique-monetaire/taux-dinteret/"
    URL_BONS_BRH = "https://www.brh.ht/politique-monetaire/bons-brh/"
    URL_RESERVES = "https://www.brh.ht/politique-monetaire/reserves-obligatoires/"

    # Supervision / Surveillance
    URL_SURVEILLANCE_BANQUES = "https://www.brh.ht/surveillance/banques/"
    URL_SURVEILLANCE_CAISSES = "https://www.brh.ht/surveillance/caisses-populaires/"
    URL_SURVEILLANCE_MICROFINANCE = "https://www.brh.ht/surveillance/microfinance/"

    # Publications & Circulaires
    URL_PUBLICATIONS = "https://www.brh.ht/publications/"
    URL_CIRCULAIRES = "https://www.brh.ht/circulaires/"
    URL_NORMES_PRUDENTIELLES = "https://www.brh.ht/circulaires/normes-prudentielles/"

    # Indicateurs dynamiques accessibles via boutons / JS
    DYNAMIC_INDICATOR_KEYWORDS = {
        "inflation": "CPI_HTI",
        "taux de change": "USD_HTG_REF",
        "taux": "USD_HTG_REF",
        "usd": "USD_HTG_REF",
        "eur": "EUR_HTG",
        "reserve": "RESERVES_HTI",
        "réserves": "RESERVES_HTI",
        "m3": "M3_HTI",
        "masse monétaire": "M3_HTI",
        "bons": "BONS_BRH",
        "balance": "BALANCE_PAIEMENTS",
        "déficit": "DEFICIT_BUDGET",
        "chômage": "UNEMPLOYMENT",
        "population": "POPULATION",
        "fdI": "FDI",
        "circulaires": "CIRCULAIRES_BRH"
    }

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Effectue la requête HTTP et parse le HTML."""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"[BRH] Failed to fetch {url}: {e}")
            return None

    # ─────────────────────────────────────────────────────────────
    # 1. TAUX DU JOUR (données HTML directes)
    # ─────────────────────────────────────────────────────────────

    def fetch_exchange_rate(self) -> List[DataPoint]:
        """Scrape le taux de référence USD/HTG et EUR/HTG depuis la page Taux du Jour."""
        logger.info("[BRH] Scraping Taux du Jour...")
        soup = self._get_soup(self.URL_TAUX_DU_JOUR)
        if not soup:
            return []

        results = []
        today = date.today()

        # Recherche des tables ou divs contenant les taux
        try:
            # Le site BRH affiche généralement une table avec les taux de change
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    if not cells:
                        continue

                    # Chercher les lignes contenant USD, EUR, DOP (Peso Dom.)
                    row_text = " ".join(cells).lower()

                    if "usd" in row_text or "dollar" in row_text:
                        val = self._parse_first_float(cells)
                        if val:
                            results.append(DataPoint(
                                indicator_code="USD_HTG_REF",
                                country_code="HTI",
                                value=val,
                                date_value=today,
                                source_name="BRH",
                                status="REEL"
                            ))
                    elif "eur" in row_text or "euro" in row_text:
                        val = self._parse_first_float(cells)
                        if val:
                            results.append(DataPoint(
                                indicator_code="EUR_HTG",
                                country_code="HTI",
                                value=val,
                                date_value=today,
                                source_name="BRH",
                                status="REEL"
                            ))

            # Fallback : chercher les valeurs dans des éléments texte spécifiques
            if not results:
                # Cherche des patterns communs pour les taux
                rate_divs = soup.find_all(["div", "span", "td", "p"],
                                          string=lambda t: t and "130" in t or "131" in t if t else False)
                for div in rate_divs:
                    val = self._parse_first_float([div.get_text(strip=True)])
                    if val and 100 < val < 250:  # Plage réaliste pour USD/HTG
                        results.append(DataPoint(
                            indicator_code="USD_HTG_REF",
                            country_code="HTI",
                            value=val,
                            date_value=today,
                            source_name="BRH",
                            status="REEL"
                        ))
                        break

        except Exception as e:
            logger.error(f"[BRH] Error parsing exchange rates: {e}")

        logger.info(f"[BRH] Found {len(results)} exchange rate points")
        return results

    def fetch_dynamic_indicators(self, requested_indicators: List[str]) -> List[DataPoint]:
        """Récupère les indicateurs qui sont accessibles via boutons/onglets dynamiques"""
        logger.info("[BRH] Scraping dynamic indicators from interactive pages...")
        results: List[DataPoint] = []
        pages = [
            self.URL_STATS_MONNAIE,
            self.URL_STATS_SECTEUR_REEL,
            self.URL_STATS_BDP,
            self.URL_STATS_FINANCES_PUB,
            self.URL_TAUX_INTERET,
            self.URL_BONS_BRH,
            self.URL_RESERVES,
        ]

        for page_url in pages:
            soup = self._get_soup(page_url)
            if not soup:
                continue

            results.extend(self._scrape_page_for_indicators(soup, requested_indicators))

            # repérer également les boutons qui chargent dynamiquement des sections via JS
            for target_url in self._extract_interactive_urls(soup):
                if target_url.startswith("/"):
                    target_url = self.BASE_URL + target_url
                if not target_url.startswith("http"):
                    continue

                if target_url == page_url:
                    continue

                target_soup = self._get_soup(target_url)
                if target_soup:
                    results.extend(self._scrape_page_for_indicators(target_soup, requested_indicators))

        unique = { (dp.indicator_code, dp.date_value, dp.value): dp for dp in results }
        final_results = list(unique.values())
        logger.info(f"[BRH] Dynamic indicator scrape returns {len(final_results)} points")
        return final_results

    def _extract_interactive_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extrait URL d'action de boutons/ancres pouvant nécessiter un click JavaScript."""
        urls: List[str] = []

        for tag in soup.find_all(True):
            # lien direct
            if tag.name == "a" and tag.get("href"):
                href = tag.get("href").strip()
                if href and href not in urls and (href.startswith("http") or href.startswith("/")):
                    urls.append(href)

            # onclick JS
            onclick = tag.get("onclick")
            if onclick:
                parsed = self._parse_js_button_link(onclick)
                if parsed and parsed not in urls:
                    urls.append(parsed)

            # data-url custom (comportement JS moderne)
            data_url = tag.get("data-url") or tag.get("data-href")
            if data_url:
                data_url = data_url.strip()
                if data_url and data_url not in urls:
                    urls.append(data_url)

        return urls

    def _parse_js_button_link(self, onclick: str) -> Optional[str]:
        """Analyse un attribut onclick pour en extraire un URL si présent."""
        # Patterns communs comme location.href, window.location, window.open
        patterns = [
            r"location\.href\s*=\s*['\"]([^'\"]+)['\"]",
            r"window\.location\s*=\s*['\"]([^'\"]+)['\"]",
            r"window\.open\(\s*['\"]([^'\"]+)['\"]",
            r"document\.location\s*=\s*['\"]([^'\"]+)['\"]"
        ]
        for p in patterns:
            m = re.search(p, onclick)
            if m:
                return m.group(1)

        # fallback : chercher un chemin relatif dans la chaîne
        m = re.search(r"['\"](/[^'\"]+)['\"]", onclick)
        return m.group(1) if m else None

    def _lookup_indicator_code_from_text(self, text: str) -> Optional[str]:
        """Déduit un code d'indicateur BRH à partir d'un texte de page / URL."""
        normalized = text.lower()
        for k, code in self.DYNAMIC_INDICATOR_KEYWORDS.items():
            if k in normalized:
                return code
        return None

    def _scrape_page_for_indicators(self, soup: BeautifulSoup, requested_indicators: List[str]) -> List[DataPoint]:
        """Parse le contenu d'une page pour récupérer des indicateurs potentiels en table/html."""
        results: List[DataPoint] = []
        today = date.today()

        # Rechercher les tables avec des indicateurs potentiels
        tables = soup.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
                if not cells:
                    continue

                row_text = " ".join(cells).lower()
                indicator_code = self._lookup_indicator_code_from_text(row_text)
                if not indicator_code:
                    continue

                if requested_indicators and indicator_code not in requested_indicators:
                    continue

                value = self._parse_first_float(cells)
                if value is None:
                    continue

                results.append(DataPoint(
                    indicator_code=indicator_code,
                    country_code="HTI",
                    value=value,
                    date_value=today,
                    source_name="BRH",
                    status="REEL"
                ))

        # En complément, chercher dans les blocs <p>, <span> qui mentionnent les mots clés.
        candidates = soup.find_all(["p", "span", "div"], string=True)
        for block in candidates:
            text = block.get_text(strip=True)
            indicator_code = self._lookup_indicator_code_from_text(text)
            if not indicator_code or (requested_indicators and indicator_code not in requested_indicators):
                continue

            value = self._parse_first_float([text])
            if value is None:
                continue

            results.append(DataPoint(
                indicator_code=indicator_code,
                country_code="HTI",
                value=value,
                date_value=today,
                source_name="BRH",
                status="REEL"
            ))

        return results

    # ─────────────────────────────────────────────────────────────
    # 2. STATISTIQUES (liens vers PDFs et pages de données)
    # ─────────────────────────────────────────────────────────────

    def fetch_stats_links(self) -> List[Dict[str, str]]:
        """Scrape les liens PDF et données disponibles dans la section Statistiques."""
        logger.info("[BRH] Scraping Statistiques PDF links...")

        stat_pages = [
            ("Monnaie", self.URL_STATS_MONNAIE),
            ("Secteur Réel", self.URL_STATS_SECTEUR_REEL),
            ("Balance des Paiements", self.URL_STATS_BDP),
            ("Finances Publiques", self.URL_STATS_FINANCES_PUB),
        ]

        all_links = []
        for category, url in stat_pages:
            soup = self._get_soup(url)
            if not soup:
                continue
            links = self._extract_pdf_links(soup, category)
            all_links.extend(links)
            logger.info(f"[BRH] Found {len(links)} links in {category}")

        return all_links

    # ─────────────────────────────────────────────────────────────
    # 3. POLITIQUE MONÉTAIRE
    # ─────────────────────────────────────────────────────────────

    def fetch_monetary_policy_links(self) -> List[Dict[str, str]]:
        """Scrape les documents de politique monétaire (taux d'intérêt, bons BRH, etc.)."""
        logger.info("[BRH] Scraping Politique Monétaire links...")

        pages = [
            ("Taux Intérêt", self.URL_TAUX_INTERET),
            ("Bons BRH", self.URL_BONS_BRH),
            ("Réserves Obligatoires", self.URL_RESERVES),
        ]

        all_links = []
        for category, url in pages:
            soup = self._get_soup(url)
            if not soup:
                continue
            links = self._extract_pdf_links(soup, category)
            all_links.extend(links)

        return all_links

    # ─────────────────────────────────────────────────────────────
    # 4. SUPERVISION / SURVEILLANCE
    # ─────────────────────────────────────────────────────────────

    def fetch_supervision_links(self) -> List[Dict[str, str]]:
        """Scrape les rapports de supervision du secteur bancaire et microfinance."""
        logger.info("[BRH] Scraping Supervision links...")

        pages = [
            ("Banques", self.URL_SURVEILLANCE_BANQUES),
            ("Caisses Populaires", self.URL_SURVEILLANCE_CAISSES),
            ("Microfinance", self.URL_SURVEILLANCE_MICROFINANCE),
        ]

        all_links = []
        for category, url in pages:
            soup = self._get_soup(url)
            if not soup:
                continue
            links = self._extract_pdf_links(soup, category)
            all_links.extend(links)

        return all_links

    # ─────────────────────────────────────────────────────────────
    # 5. PUBLICATIONS & CIRCULAIRES
    # ─────────────────────────────────────────────────────────────

    def fetch_publications(self) -> List[Dict[str, Any]]:
        """Scrape les publications officielles de la BRH (articles, rapports)."""
        logger.info("[BRH] Scraping Publications...")
        soup = self._get_soup(self.URL_PUBLICATIONS)
        if not soup:
            return []

        publications = []
        # Cherche les articles dans les cartes/posts WordPress typiques
        articles = soup.find_all(["article", "div"], class_=lambda c: c and
                                 any(k in c for k in ["post", "entry", "item", "card"]))

        for article in articles[:20]:  # Limite à 20 dernières publications
            title_el = article.find(["h1", "h2", "h3", "h4", "a"])
            title = title_el.get_text(strip=True) if title_el else "Sans titre"
            link_el = article.find("a", href=True)
            link = link_el["href"] if link_el else ""
            if link and not link.startswith("http"):
                link = self.BASE_URL + link

            date_el = article.find(["time", "span"], class_=lambda c: c and "date" in c.lower() if c else False)
            pub_date = date_el.get_text(strip=True) if date_el else ""

            publications.append({
                "title": title,
                "url": link,
                "date": pub_date,
                "category": "Publication BRH",
                "type": "PDF" if ".pdf" in link.lower() else "Article"
            })

        # Aussi chercher les liens directs
        pdf_links = self._extract_pdf_links(soup, "Publications")
        for pdf in pdf_links:
            if pdf not in publications:
                publications.append(pdf)

        return publications

    def fetch_circulaires(self) -> List[Dict[str, Any]]:
        """Scrape la liste des circulaires et normes prudentielles de la BRH."""
        logger.info("[BRH] Scraping Circulaires...")
        soup = self._get_soup(self.URL_CIRCULAIRES)
        if not soup:
            return []

        links = self._extract_pdf_links(soup, "Circulaires")

        # Aussi les normes prudentielles
        soup2 = self._get_soup(self.URL_NORMES_PRUDENTIELLES)
        if soup2:
            links.extend(self._extract_pdf_links(soup2, "Normes Prudentielles"))

        return links

    # ─────────────────────────────────────────────────────────────
    # MÉTHODE COMPLÈTE : tout scraper en une fois
    # ─────────────────────────────────────────────────────────────

    def fetch_all(self) -> Dict[str, Any]:
        """Lance le scraping complet de toutes les sections BRH."""
        logger.info("[BRH] ===== Démarrage du scraping complet =====")

        results = {
            "exchange_rates": self.fetch_exchange_rate(),
            "statistiques": self.fetch_stats_links(),
            "politique_monetaire": self.fetch_monetary_policy_links(),
            "supervision": self.fetch_supervision_links(),
            "publications": self.fetch_publications(),
            "circulaires": self.fetch_circulaires(),
        }

        total_items = sum(len(v) for v in results.values())
        logger.info(f"[BRH] ===== Scraping terminé : {total_items} éléments collectés =====")
        return results

    # ─────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ─────────────────────────────────────────────────────────────

    def _extract_pdf_links(self, soup: BeautifulSoup, category: str) -> List[Dict[str, str]]:
        """Extrait tous les liens PDF et documents dans une page."""
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if not text:
                continue

            # Lien PDF ou document Word
            is_doc = any(ext in href.lower() for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx"])
            if not is_doc:
                continue

            if not href.startswith("http"):
                href = self.BASE_URL + href

            links.append({
                "title": text,
                "url": href,
                "category": category,
                "type": "PDF" if ".pdf" in href.lower() else "Excel"
            })
        return links

    def _parse_first_float(self, cells: List[str]) -> Optional[float]:
        """Extrait le premier float valide depuis une liste de cellules texte."""
        for cell in cells:
            cleaned = cell.replace(" ", "").replace("\xa0", "")
            # Cherche un nombre flottant (ex: 14.6, 1,234.50, 14.6%)
            # inclut aussi des milliers sur le format 1,234.50 ou 1.234,50
            matches = re.findall(r"-?[0-9][0-9\.,]*[0-9]", cleaned)
            for m in matches:
                candidate = m

                if candidate.count(",") > 0 and candidate.count(".") > 0:
                    # Format mixte milliers + décimal
                    if candidate.index(",") < candidate.index("."):
                        candidate = candidate.replace(",", "")
                    else:
                        candidate = candidate.replace(".", "").replace(",", ".")
                elif candidate.count(",") > 0:
                    # Si l'unique virgule correspond à 3 chiffres à droite, considérer comme séparateur de milliers
                    parts = candidate.split(",")
                    if len(parts[-1]) == 3 and all(len(p) == 3 for p in parts[1:]):
                        candidate = candidate.replace(",", "")
                    else:
                        candidate = candidate.replace(",", ".")

                candidate = candidate.replace("%", "")

                try:
                    val = float(candidate)
                    if val > 0:
                        return val
                except ValueError:
                    continue
        return None
