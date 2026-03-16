from bs4 import BeautifulSoup
from data_ingestion.extractors.brh.scrapers import BRHScraper
html='<html><body><table><tr><th>Indicateur</th><th>Valeur</th></tr><tr><td>Inflation</td><td>14.6%</td></tr><tr><td>Réserves</td><td>1,234.5</td></tr></table></body></html>'
scraper=BRHScraper()
soup=BeautifulSoup(html,'html.parser')
results=scraper._scrape_page_for_indicators(soup,['CPI_HTI','RESERVES_HTI'])
print([(dp.indicator_code, dp.value) for dp in results])
