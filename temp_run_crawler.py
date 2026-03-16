from data_ingestion.extractors.brh.crawler import BRHSiteCrawler

crawler = BRHSiteCrawler(max_depth=2, max_pages=40)
crawler.crawl()
print('visited', len(crawler.visited))
print('resources', len(crawler.resource_metadata))
for r in crawler.resource_metadata[:20]:
    print(r.source_url, r.file_type, r.status, r.category, r.local_path)
