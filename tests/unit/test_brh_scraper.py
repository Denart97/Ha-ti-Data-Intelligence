import pytest
from bs4 import BeautifulSoup
from data_ingestion.extractors.brh.scrapers import BRHScraper


def test_parse_js_button_link():
    scraper = BRHScraper()
    onclick = "javascript:location.href='/statistiques/monnaie/?tab=inflation'"
    assert scraper._parse_js_button_link(onclick) == "/statistiques/monnaie/?tab=inflation"

    onclick2 = "window.open('https://www.brh.ht/statistiques/monnaie/');"
    assert scraper._parse_js_button_link(onclick2) == "https://www.brh.ht/statistiques/monnaie/"


def test_extract_interactive_urls_from_html():
    html = '''
    <html><body>
      <a href="/statistiques/monnaie/">Monnaie</a>
      <button onclick="location.href='/statistiques/monnaie/?tab=reserves'">Réserves</button>
      <div data-url="https://www.brh.ht/politique-monetaire/reserves-obligatoires/"></div>
    </body></html>'''
    scraper = BRHScraper()
    soup = BeautifulSoup(html, 'html.parser')

    urls = scraper._extract_interactive_urls(soup)
    assert '/statistiques/monnaie/' in urls
    assert '/statistiques/monnaie/?tab=reserves' in urls
    assert 'https://www.brh.ht/politique-monetaire/reserves-obligatoires/' in urls


def test_scrape_page_for_indicators_tables():
    html = '''
    <html><body>
      <table>
        <tr><th>Indicateur</th><th>Valeur</th></tr>
        <tr><td>Inflation</td><td>14.6%</td></tr>
        <tr><td>Réserves</td><td>1,234.5</td></tr>
      </table>
    </body></html>
    '''
    scraper = BRHScraper()
    soup = BeautifulSoup(html, 'html.parser')
    results = scraper._scrape_page_for_indicators(soup, ['CPI_HTI', 'RESERVES_HTI'])

    assert any(dp.indicator_code == 'CPI_HTI' and dp.value == 14.6 for dp in results)
    assert any(dp.indicator_code == 'RESERVES_HTI' and dp.value == 1234.5 for dp in results)
