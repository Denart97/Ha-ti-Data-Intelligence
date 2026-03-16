# Conception du Module d'Extraction : IHSI (Institut Haïtien de Statistique et d'Informatique)

Ce document détaille la stratégie d'extraction pour l'IHSI. C'est le module le plus hétérogène, traitant à la fois de l'inflation mensuelle, des recensements décennaux et des données géospatiales.

---

## 1. Cartographie des Rubriques du Site (Thematic Mapping)

Le site de l'IHSI est structuré par domaines thématiques. Nous utilisons un dictionnaire de routage pour cibler les dossiers critiques :
*   **Économie (Conjoncture) :** IPC (Inflation), Comptes Nationaux (PIB), Commerce Extérieur.
*   **Démographie :** Estimations et projections de population, Recensements (RGPH).
*   **Social :** Conditions de vie (ECVMAS), Emploi, Santé/Éducation.
*   **Géographie :** Découpage territorial, cartes, limites administratives.

## 2. Stratégie de Détection des Pages de Données

*   **Pattern Matching :** Surveillance des URLs contenant `rubriques.asp`, `publications.asp` ou des répertoires thématiques.
*   **Discovery Engine :** Utilisation d'un crawler hebdomadaire qui liste les nouveaux titres dans les rubriques "Flash Inflation" et "Comptes Nationaux".
*   **Lien vers Taxonomie :** Chaque nouvelle page identifiée est associée à un `grand_domaine` de notre taxonomie pour orienter les transformations.

## 3. Stratégie de Téléchargement des Publications

*   **Extraction PDF :** Analyse des balises `<a>` pour isoler les liens de documents.
*   **Metadata Harvesting :** Extraire la date de publication et le titre directement depuis le texte du lien ou la balise de titre adjacente.
*   **Versioning Sécurisé :** Les documents de l'IHSI (notamment les résultats de recensements) sont massifs. Téléchargement asynchrone avec vérification d'intégrité (Size + Hash).

## 4. Stratégie d'Extraction des Tableaux et Séries

L'IHSI publie majoritairement via des bulletins PDF contenant des grilles complexes.
*   **Hybrid Parsing :**
    - **Tabulaire PDF :** Utilisation de `Camelot` avec l'option `lattice=True` (pour les PDF avec lignes de tableaux) ou `stream=True` (pour les tableaux sans bordures).
    - **Séries Longues :** Si disponible, privilégier le téléchargement des fichiers Excel souvent cachés dans les sous-rubriques, car ils limitent les erreurs d'OCR.
*   **Unpivot Automatique :** Transformation des rapports "wide" (Années en colonnes) en format "long" standard HDI.

## 5. Stratégie d'Intégration des Données Géographiques (GIS)

L'IHSI est le garant du référentiel territorial.
*   **Formats :** Récupération des fichiers `.shp` (Shapefiles) ou `.geojson`.
*   **Hiérarchie Territoriale :** Construction d'une table de référence `territoires` : 
    `Département > Arrondissement > Commune > Section Communale`.
*   **Normalisation Spatiale :** Conversion systématique en projection `WGS 84 (EPSG:4326)` pour compatibilité avec les librairies web (Leaflet, Mapbox).

## 6. Normalisation par Thème et Niveau Géo

*   **Granularité :** Marquer chaque donnée avec son `geo_level` (National vs Départemental).
*   **Codes Géo-Statistiques :** Utilisation du Code Officiel Géographique de l'IHSI (ex: `01` pour l'Ouest, `0111` pour Port-au-Prince) comme clé Pivot pour les jointures spatiales.

## 7. Stratégie de Qualité (Audit)

*   **Vérification de Cohérence :** La population totale (Calculée par somme des départements) doit être égale à la population nationale déclarée (Marge d'erreur < 0.1%).
*   **Validation Temporelle :** Pas de "trous" dans les séries mensuelles de l'IPC.
*   **Alertes Rupture :** Notification si le nombre de communes change (rare mais structurel).

## 8. Stratégie de Stockage

*   **Structuré :** Données chiffrées -> PostgreSQL (`valeurs_indicateurs`).
*   **Spatiale :** Limites géographiques -> Extension `PostGIS`.
*   **Textuel :** Rapports méthodologiques -> ChromaDB pour le RAG.

---

## 9. Architecture du Code (Fichiers)

Module : `data_ingestion/sql_loaders/ihsi/`

1.  **`catalog.py`** : Cartographie des URLs IHSI et gestion des métadonnées thématiques.
2.  **`crawler.py`** : Détecte les nouveaux bulletins et gère les sessions de téléchargement.
3.  **`stats_parser.py`** : Spécialisé dans l'extraction des tableaux (PDF/Excel) pour l'inflation et le PIB.
4.  **`census_parser.py`** : Gestion spécifique des gros volumes de données de recensement (traitement par batch).
5.  **`spatial_loader.py`** : Intègre les fichiers Shapefiles dans PostGIS via `GeoPandas`.
6.  **`main_ihsi_etl.py`** : Orchestration globale du flux IHSI.
7.  **`config/ihsi_geo_codes.yaml`** : Référentiel des codes départementaux et communaux.
