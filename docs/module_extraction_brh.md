# Conception du Module d'Extraction : BRH (Banque de la République d'Haïti)

Ce document détaille la stratégie d'extraction pour la BRH. Contrairement aux sources internationales (BM/FMI), la BRH nécessite une approche de "Web Intelligence" basée sur le scraping et le parsing de documents non structurés.

---

## 1. Stratégie d'Exploration du Site (Crawling)

Le site `brh.ht` est la source de vérité. L'exploration suit une approche par "Seeds" (Points d'entrée) :
*   **Seed Statistiques :** Pages de taux de change, taux d'intérêt, inflation.
*   **Seed Publications :** Rapports annuels, notes sur la politique monétaire, bulletins trimestriels.
*   **Méthode :** Utilisation de `Playwright` (pour gérer le rendu JS potentiel) ou `httpx` + `BeautifulSoup` pour la rapidité.
*   **Fréquence de crawl :** Quotidienne pour les taux de change, Hebdomadaire pour les publications.

## 2. Détection des Pages Statistiques

*   **Identification :** Recherche de patterns d'URL (ex: `/statistiques/`) et de mots-clés dans les titres (`<h1>`, `<h2>`).
*   **Cartographie :** Tenir à jour un fichier `brh_map.yaml` qui lie un indicateur à une URL précise du site BRH. 
    - Exemple : `taux_change_reference: https://www.brh.ht/taux-de-reference/`

## 3. Détection et Téléchargement des Publications

*   **Scraping des liens PDF :** Extraction de tous les liens finissant par `.pdf` sur les pages de publications.
*   **Détection des nouveautés (Checksum) :**
    - Calcul du hash MD5 du fichier PDF.
    - Comparaison avec la table `documents` de PostgreSQL.
    - Si le hash est nouveau -> Téléchargement et indexation RAG.
*   **Filtrage :** Ignorer les brochures marketing ou les documents administratifs non-économiques via des filtres sur le nom du fichier.

## 4. Stratégie d'Extraction des Tableaux (Data Structurée)

*   **Tableaux HTML :** Utilisation de `pandas.read_html()` pour récupérer les tableaux de change directement depuis les pages web.
*   **Tableaux dans PDF :** Utilisation de `Camelot` ou `tabula-py`.
    - **Problème :** Les PDF de la BRH changent parfois de mise en page. 
    - **Solution :** Utiliser des "Templates de Régions" (Bounding boxes) définis par version d'année dans la config.

## 5. Stratégie d'Extraction du Texte (RAG)

*   **Moteur d'extraction :** `PyMuPDF` (fitz) pour la rapidité et la préservation de l'ordre de lecture.
*   **Nettoyage sémantique :**
    - Détection et suppression des "headers" (ex: "Banque de la République d'Haïti") en haut de chaque page.
    - Reconstruction des paragraphes coupés par des sauts de page.
    - Extraction des métadonnées contextuelles (Titre du rapport, Date, Chapitre).

## 6. Stratégie de Métadonnées

Chaque extrait (Chunk ou Data Point) stocke :
- `source_url` : Lien exact de la page d'origine.
- `extraction_timestamp` : Date de la capture.
- `institutional_context` : "Officiel BRH".
- `document_type` : "Publication Trimestrielle", "Note Monétaire", etc.

## 7. Stockage des Documents et Données

*   **Fichiers Bruts (Bronze) :** Sauvegarde du PDF original dans `data/raw/brh/{yyyy-mm-dd}/`.
*   **Données SQL (Silver/Gold) :** Séries temporelles normalisées dans PostgreSQL.
*   **Vecteurs (RAG) :** Embeddings dans ChromaDB.

## 8. Gestion des Changements de Structure du Site

C'est le risque n°1 du scraping.
*   **Découpleur de Selectors :** Aucun sélecteur CSS/XPath ne doit être en dur dans le code. Ils sont dans `config/scrapers/brh_selectors.yaml`.
*   **Tests de Smoke (Auto-Audit) :** Avant de parser, le script vérifie si les éléments critiques sont présents (ex: `table.taux-reference`). S'ils ont disparu -> Envoi d'une alerte "Site structure changed".

## 9. Garde-fous Qualité

*   **Validation des Taux :** Si le taux de change varie de plus de 5% en 24h, le point est marqué comme "A Valider" et ne sort pas en production sans confirmation humaine (Alerte Risque).
*   **Validation OCR :** Si l'extraction de texte produit un taux de "déchets" (caractères non-ASCII) trop élevé -> Erreur.

---

## 10. Architecture du Code (Fichiers)

Logé dans `data_ingestion/sql_loaders/brh/` et `data_ingestion/document_loaders/brh/`.

1.  **`scrapers/web_scraper.py`** : Logique de navigation, gestion des sessions/headers, extraction HTML brut.
2.  **`scrapers/pdf_downloader.py`** : Détection des nouveaux rapports, gestion du hachage et téléchargement.
3.  **`parsers/html_parser.py`** : Convertit les tables HTML en DataFrames standardisés.
4.  **`parsers/pdf_table_extractor.py`** : Utilise Camelot pour les tableaux figés dans les notes monétaires.
5.  **`parsers/pdf_text_extractor.py`** : Prépare le texte pour le module RAG (nettoyage, chapitrage).
6.  **`brh_orchestrator.py`** : Pilote les différents scripts selon la fréquence demandée.
7.  **`config/brh_map.yaml`** : Mapping des URLs et des indicateurs.
8.  **`config/brh_selectors.yaml`** : Sélecteurs CSS/XPath pour le scraping.
