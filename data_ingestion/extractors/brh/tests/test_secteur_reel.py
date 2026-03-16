from data_ingestion.extractors.brh.pipeline import BRHPipeline


def test_secteur_reel_flow():
    pipeline = BRHPipeline()
    results = pipeline.run_navigation_and_extract('Statistiques', 'Secteur Réel')
    # Basic asserts: returns a list
    assert isinstance(results, list)

    # print summary
    print('resources found:', len(results))
