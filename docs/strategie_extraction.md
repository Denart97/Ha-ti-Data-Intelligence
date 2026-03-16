# Stratégie Globale d'Extraction des Données : Haiti Data Intelligence

Ce document détaille l'approche d'ingestion technique ("Extract"), pensée pour être robuste, maintenable et découpée source par source. 

L'extraction obéit au principe central : **Découplage absolu entre la récupération brute (Extract) et la transformation logicielle (Transform)**. Les extracteurs ne font que rapatrier la donnée dans son format natif vers une zone de transit ("Landing Zone" / Raw Data) avant normalisation.

---

## 1. Stratégie d'Extraction par Source

### 1.1 Source : Banque Mondiale (World Bank Open Data)
*   **Priorité :** Primaire (Critique).
*   **Type de donnée :** Séries temporelles macroéconomiques internationales comparables.
*   **Méthode d'Extraction :** **API REST** (utilisation du package Python officiel `wbdata` ou appels natifs via la librairie `requests`).
*   **Implémentation :** Script `extract_wb.py` qui boucle sur notre dictionnaire `taxonomie_metier.md` contenant les codes API (`NY.GDP.MKTP.CD` pour le PIB, etc.). Requête avec paramètre `country=['HTI', 'DOM']`.

### 1.2 Source : Fonds Monétaire International (FMI / IMF)
*   **Priorité :** Primaire (Structuré et Qualitatif).
*   **Type de donnée :** Indépendance financière, Dette, Rapports "Article IV".
*   **Méthode d'Extraction (Données) :** **API REST** (IMF Data Services JSON API).
*   **Méthode d'Extraction (Rapports) :** **Web Scraping / PDF Download** sur la page des publications du FMI filtrée par le Tag "Haiti".
*   **Implémentation :** Script `extract_imf_data.py` (API Builder Json) + `extract_imf_reports.py` (BeautifulSoup sur les listes de liens PDF).

### 1.3 Source : Banque de la République d'Haïti (BRH)
*   **Priorité :** Primaire ABSOLU (La source de vérité monétaire locale).
*   **Type de donnée :** Statistiques quotidiennes/mensuelles (Taux de Référence, Inflation de base, Réserves) et Bulletins PDF de la politique monétaire.
*   **Méthode d'Extraction (Données) :** **Scraping HTML / Fichiers Téléchargeables (Excel)**. La BRH ne dispose pas d'API publique REST documentée.
*   **Méthode d'Extraction (Rapports) :** Web Scraping de la section "Publications" pour les PDF.
*   **Implémentation :** 
    *   `extract_brh_stats.py`: Utilise `pandas.read_html()` ou télécharge les tableaux Excel publiés périodiquement.
    *   `extract_brh_docs.py`: Scraper les liens `.pdf` pointant vers les Notes Monétaires.

### 1.4 Source : Institut Haïtien de Statistique et d'Informatique (IHSI)
*   **Priorité :** Primaire (Uniquement pour le PIB National et l'IPC/Inflation).
*   **Type de donnée :** Indice des Prix à la Consommation (Mensuel), Comptes Nationaux (Annuel).
*   **Méthode d'Extraction :** **Fichiers PDF natifs (Tableaux imbriqués)** ou Excel si disponible sur leur nouveau site. Historiquement, l'IHSI publie sous forme de bulletins statistiques (PDF textuels avec tables).
*   **Implémentation :** `extract_ihsi.py` utilisant les librairies `tabula-py` ou `Camelot` dédiées exclusivement à la reconnaissance de grilles tabulaires figées dans des documents PDF.

---

## 2. Typologie des Méthodes d'Extraction

Afin d'industrialiser, le code est construit autour d'Interfaces Python (`BaseExtractor`).

| Mode d'Extraction | Stabilité | Effort Maintenabilité | Approche Python |
| :--- | :--- | :--- | :--- |
| **API REST JSON** | Très Haute | Très Faible | `requests`, validation de payload avec `Pydantic`. |
| **Fichier Téléchargeable (CSV/Excel)**| Moyenne | Faible | `requests.get()` direct sur l'URL, puis chargement via `pandas`. |
| **Scraping HTML (Web)**| Faible (Le site peut changer)| Très Haute | Découplage strict de la définition du DOM (DOM Selectors). Utilisation de `BeautifulSoup` ou `Playwright` si génération JS (SPA) côté source. |
| **Parsing PDF (Documents)**| Haute | Basse | `PyMuPDF` (fitz) pour le texte (RAG), extraction du hash binaire (MD5) pour détecter de nouveaux PDF. |
| **Parsing PDF (Tableaux)**| Très Faible | Extrême | `Camelot`. On utilise des coordonnées de boîtes limites (*bounding boxes*) en dur. À isoler dans des scripts très indépendants. |

---

## 3. Matrice des Risques par Source

| Source | Risque Principal d'Extraction | Mitigations Technologiques |
| :--- | :--- | :--- |
| **World Bank / FMI** | Timeout (Limit Rate API). | Implémenter des limites de requêtes (Sleep) et un mécanisme *Backoff Retry* exponentiel. |
| **BRH** | Refonte du site web cassant les regex de scraping ; structure Excel instable. | Les sélecteurs XPath/CSS doivent être déclarés en variables d'environnement (`config.py`) pour être modifiés sans toucher au code métier. Système d'alerte immédiat (`raise ScraperDOMError`). |
| **IHSI** | Pages de PDF scannées (Image textuelle) non-lisibles, format de tableau qui varie d'un mois à l'autre. | Vérification du type `.pdf` avec `pdfplumber.pages[0].chars`. Si liste vide -> c'est une image. Levée d'une alerte manuelle "Nécessite OCR lourd". Ne pas forcer l'ingestion automatique de la data structurée depuis l'image (risque de faux chiffres). |

---

## 4. Stratégie de Normalisation

Dès la sortie de l'Extracteur (qui crache de la donnée brute hétérogène), la donnée passe dans les "Transformers" selon les règles édictées dans la `strategie_normalisation`.
1.  **Pivot de la donnée :** Passage de tableaux croisés (Mois en colonnes) vers un format de base de données à plat (Tidy : `Date`, `Pays`, `Indicateur`, `Valeur`).
2.  **Mapping Taxonomie :** Validation des noms via le dictionnaire interne (`taxonomie_metier.md`).
3.  **Sanatization :** Nettoyage des chaînes textuelles dans les PDF (retrait des balises invisibles, sauts de lignes de titre, normalisation Unicode `NFC`).

---

## 5. Stratégie de Stockage DUAL (Raw vs Clean)

Architecture de type *Medallion* (Bronze/Argent/Or).

*   **Zone Raw (Landing/Bronze) :** Sauf pour les appels API légers, TOUTE source téléchargée (Fichier Excel de la BRH, PDF de l'IHSI) est physiquement enregistrée sur le serveur dans un dossier daté : `data/raw/brh/2023-11-01/bulletin.xlsx`.
    *   *But :* Si une erreur survient dans l'étape de transformation/nettoyage, nous pouvons relancer le script sur le fichier stocké localement sans engorger les serveurs de la BRH avec de multiples téléchargements.
*   **Zone Processed (Clean/Or) :** Une fois le DataFrame validé et nettoyé, le stockage final s'effectue dans **PostgreSQL** (`valeurs_indicateurs`) ou **ChromaDB** pour les vecteurs.

---

## 6. Stratégie de Logs (Traçabilité ETL)

Chaque exécution d'astractor génère une trace structurée envoyée vers un fichier de log JSON (`logs/etl_extraction.jsonl`), permettant un monitoring via des agrégateurs (ex: Elastic/Kibana ou console basique).

**Payload du Log d'Extraction standardisé :**
```json
{
  "timestamp": "2023-10-25T14:30:22Z",
  "job_name": "extract_brh_taux_change",
  "status": "SUCCESS",
  "source_type": "HTML_SCRAPE",
  "records_extracted": 31,
  "execution_time_ms": 1450,
  "error_message": null
}
```

---

## 7. Plan de Reprise sur Erreur (Error Recovery)

1.  **Mécanisme Idempotent :** Un script d'extraction peut être lancé 1 ou 100 fois par jour ; s'il trouve les mêmes données distantes, il mettra à jour la base localement sans créer de doublons (grâce au `ON CONFLICT DO UPDATE` d'Hypertable ou SQL).
2.  **Retry Global Automatisé :** Wrapper chaque appel réseau externe sous la loge `@retry` (package `tenacity`).
    ```python
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def fetch_api_with_retry(url): ...
    ```
3.  **Circuit Breaker (Coupe-circuit) :** Si la source (ex: site de l'IHSI) renvoie des erreurs HTTP 500 consécutives (site hors ligne), marquer la tâche comme `FAILED_UPSTREAM` et suspendre les appels vers cette source (sleep 24h) pour éviter d'aggraver leur serveur ou d'être banni pour scraping abusif (IP Ban).
4.  **Notification :** Toute erreur critique d'extraction (`BeautifulSoup` ne trouve plus la table HTML suite à la refonte du site BRH) envoie instantanément une alerte Email/Slack au Data Engineer avec la stacktrace. L'ancienne donnée de la veille reste affichée sur le Dashboard sans être corrompue.
