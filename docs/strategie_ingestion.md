# Stratégie d'Ingestion des Données : Haiti Data Intelligence

Ce document définit les pipelines ETL (Extract, Transform, Load) pour chaque type de ressource de la plateforme. L'objectif est de garantir une ingestion industrialisable, résiliente et traçable.

---

## 1. Données Structurées (Séries Macroéconomiques)

Concerne les séries temporelles issues de la Banque Mondiale (API), BRH (CSV/Excel) ou IHSI (Tableaux PDF/Excel).

*   **1. Fréquence :** Mensuelle (pour l'inflation, change) à Annuelle (PIB). Déclenchement par un *cron job* programmé.
*   **2. Mode de récupération :**
    *   *Push/Pull API :* Script Python utilisant des packages clients (`wbdata` pour la Banque Mondiale) ou la librairie `requests`.
    *   *Scraping ciblé :* Téléchargement de fichiers Excel statiques sur le site de la BRH via parsing de la page HTML (`BeautifulSoup`).
*   **3. Validation :**
    *   Vérification des types (Pandas/Pydantic) : *Est-ce bien un float ? L'année est-elle au format YYYY ?*
    *   *Anomaly Detection :* Un delta de +500% sur un mois d'inflation d'une année sur l'autre lève un "Warning".
*   **4. Normalisation :**
    *   Alignement strict des dates sur le format YYYY-MM-DD.
    *   Standardisation des codes pays au format ISO-Alpha3 (`HTI`).
    *   Dédoublonnage et alignement des indices (Pivot en structure "Tidy Data" : Colonnes `Pays, Date, Indicateur, Valeur`).
*   **5. Stockage :** Insertion SQL "Upsert" (`INSERT ... ON CONFLICT DO UPDATE`) dans la table `valeurs_indicateurs` (PostgreSQL).
*   **6. Logs :** Traces d'exécution enregistrées (ex: `{ "job": "WB_extract", "lines_added": 12, "errors": 0 }`).
*   **7. Reprise sur Erreur (Retry Strategy) :**
    *   Si échec réseau (Timeout API) : Retries exponentiels (1m, 5m, 15m) (utilisation de la librairie `Tenacity`).
    *   Si échec de validation schéma : Le script s'arrête en logguant une erreur fatale (`CRITICAL`) sur Slack/Email. Pas d'insertion corrompue dans la DB.

## 2. Documents et Rapports (Ingestion RAG)

Concerne les PDF de la BRH, Banque Mondiale, FMI.

*   **1. Fréquence :** Trimestrielle (Rapports) ou Mensuelle.
*   **2. Mode de récupération :**
    *   Scraping de la page "Publications" de la BRH pour détecter de nouveaux liens `.pdf` via le hash du fichier (pas de re-téléchargement si hash identique).
*   **3. Validation :**
    *   Validation MIME Type (bien un `application/pdf`).
    *   Validation lisibilité : Si OCR impossible ou texte extrait < 100 mots (ex: PDF entièrement scanné en image corrompue), le fichier est rejeté.
*   **4. Normalisation (Chunking & Parsing) :**
    *   Extraction du texte avec `PyMuPDF` ou `pdfplumber`.
    *   Nettoyage : Suppression des en-têtes/pieds de page récurrents et des numéros de page isolés.
    *   Découpage sémantique (Chunking RecursiveCharacterTextSplitter) de ~500-1000 tokens avec "overlap" de 10% pour ne pas couper le contexte.
    *   Vectorisation via appel API (ex: `text-embedding-v3`).
*   **5. Stockage :**
    *   Le texte pur (`texte_contenu`) est stocké dans PostgreSQL (`chunks_documentaires`).
    *   Les vecteurs d'embeddings vont dans ChromaDB avec les ID correspondants.
    *   Le PDF original brut est placé sur un stockage objet "Cold" (AWS S3 ou dossier local `data/raw/`).
*   **6. Logs :** `{ "job": "BRH_pdf_ingest", "doc": "Q3_2023.pdf", "chunks_created": 150 }`.
*   **7. Reprise sur Erreur :**
    *   Si plantage lors du découpage ou de l'appel à l'API d'embedding (erreur RateLimit), la transaction globale échoue. Le document est flagué "FAILED" et la tâche est relancée au prochain batch (Idempotence de l'ingestion document).

## 3. Ingestion des Métadonnées (Taxonomie)

L'injection du dictionnaire métier et des règles de synonymes.

*   **1. Fréquence :** Rare / À la demande (lorsque la taxonomie `taxonomie_metier.md` est mise à jour).
*   **2. Mode de récupération :** Chargement manuel ou automatique depuis un fichier de configuration YAML ou Markdown.
*   **3. Validation :** Pydantic Schema Validator pour vérifier que chaque indicateur a au moins un `nom` et un `code`.
*   **4. Normalisation :** Conversion en entités SQL.
*   **5. Stockage :** Tables `indicateurs` et `grand_domaines` de PostgreSQL.
*   **6. Logs :** Simple log applicatif de démarrage (Admin Action).
*   **7. Reprise sur Erreur :** En cas d'échec de mise à jour, rollback SQL (conservation de l'ancienne taxonomie).

## 4. Jeux Géographiques et Cartographiques (V2/V3)

Concerne les fichiers Shapefiles (.shp, .geojson) définissant les limites départementales.

*   **1. Fréquence :** Quasi-statique (mise à jour annuelle ou si création de commune).
*   **2. Mode de récupération :** Dépôts manuels asynchrones (Upload via Interface Admin par l'analyste Data).
*   **3. Validation :** Vérification de la géométrie via `GeoPandas` (Polygones valides, projection EPSG 4326/WGS84).
*   **4. Normalisation :** Standardisation des noms des communes, typologie UTF-8 propre.
*   **5. Stockage :** En base `PostGIS` (extension PostgreSQL pour les types géométriques).
*   **6. Logs :** Volume des géométries ingérées.
*   **7. Reprise sur Erreur :** L'interface admin renvoie directement l'erreur de validation topologique à l'utilisateur lors de l'upload.

## 5. Sources de Veille (V3 : Alertes & Newsfeed)

Concerne les requêtes d'alerte, de fils RSS (ReliefWeb) ou de la presse financière.

*   **1. Fréquence :** Quotidienne ou Temps-Réel (Triggers Webhook).
*   **2. Mode de récupération :** Parseur de flux RSS ou API d'Alerte (News API).
*   **3. Validation :** Filtrage sur mots-clés spécifiques ("Haïti", "Économie", "Inflation"). Exclusion des articles "Opinion".
*   **4. Normalisation :** Extraction du titre, de la date, de l'auteur et du lien avec formatage JSON standard.
*   **5. Stockage :** Base de données SQL d'alerte (`news_alerts`) structurée pour suppression automatique après 30 jours (Retention Policy = "Ephémère").
*   **6. Logs :** Taux de filtrage (ex: 100 articles vus, 3 retenus).
*   **7. Reprise sur Erreur :** Si flux RSS inaccessible, le job cron skip l'itération et retente à la prochaine planification sans notification majeure (Fail Silently), évitant la fatigue d'alertes pour le développeur.
