# Architecture Technique : Haiti Data Intelligence

Ce document traduit l'architecture fonctionnelle en recommandations technologiques concrètes, en construisant un backend modulaire (Python) et un frontend interactif. Il présente les choix pour le MVP tout en gardant une voie d'évolution vers la V2.

---

## 1. Stack Technologique Recommandée (MVP & Cible)

### 1.1 Backend & API (Le Cœur)
*   **Langage :** `Python 3.11+` (Incontournable pour l'écosystème Data et IA).
*   **Framework API :** `FastAPI`.
    * *Justification :* Plus moderne, rapide (asynchrone) et type-safe (Pydantic) que Flask. Il génère automatiquement la documentation Swagger, indispensable pour exposer nos données statistiques.

### 1.2 Persistance des Données (Stockage)
*   **Base Relationnelle (Données Structurées) :** `PostgreSQL` (MVP local / Prod AWS RDS).
    * *Justification :* Robuste pour les séries temporelles, supporte le SQL complexe (pour le Data Engine), et extension possible vers PostGIS si nous intégrons des cartes plus tard. Pour dev rapide MVP, `SQLite` peut suffire initialement, mais le code SQL (via SQLAlchemy/SQLModel) sera agnostique.
*   **Base Vectorielle (Documents RAG) :** `ChromaDB` (Local/MVP) évoluant vers un cluster hébergé en V2.
    * *Justification FAISS vs Chroma :* FAISS est excellent, ultra-rapide mais très bas niveau. Chroma est une base complète "AI-native" gérant très bien les métadonnées requises pour notre système de citation strict.

### 1.3 Moteurs et Pipelines (Business Logic)
*   **Orchestrateur IA / RAG :** `LangChain` ou `LlamaIndex` combiné aux modèles Azure OpenAI (`gpt-4o-mini`) ou Anthropic (`Claude 3.5 Sonnet`).
*   **Moteur Analytique (Text-to-SQL) :** `SQLAlchemy` classique intégré dans l'API FastAPI, ou utilisation d'un Agent orienté Data (si requêtes complexes en V2).
*   **Ingestion Documentaire (PDF) :** `PyMuPDF` ou `pdfplumber` pour l'extraction de texte.

### 1.4 Frontend (Interface Utilisateur)
*   **MVP (Vitesse & Analyse) :** `Streamlit`.
    * *Justification :* Permet de construire un Dashboard analytique et un Chatbot hybride en 1 semaine en pur Python, sans overhead de développement Frontend. Idéal pour pivoter, ajuster les graphiques et valider le besoin auprès des "early adopters".
*   **Cible V2 (Scale & B2B) :** `Next.js` (React).
    * *Justification :* Streamlit montre ses limites concurrentielles avec des centaines d'utilisateurs. Next.js permettra une UI sur-mesure, très performante et intégrable dans des SI d'entreprise sécurisés.

### 1.5 Transverse (DevOps, Config, Tests)
*   **Configuration :** Variables d'environnement (`.env`) via `Pydantic Settings` de FastAPI.
*   **Dépendances :** `Poetry` ou `uv` pour un environnement Python déterministe.
*   **Tests :** `pytest` (Tests unitaires backend) + `Ragas` (Framework pour l'évaluation métrique du RAG : pertinence, fidélité).
*   **Logs & Monitoring :** `logging` natif Python formaté en JSON. `Prometheus`/`Grafana` pour monitorer les taux d'erreur API. Tracing de l'IA via `LangSmith` ou `Phoenix`.

---

## 2. Diagramme d'Architecture Technique (MVP)

```text
                                +-----------------------------+
                                |  UI : Streamlit (App.py)    |
                                +-----------------------------+
                                     ^                   |
                    (Charts & JSON)  |                   | (User Query, REST API)
                                     v                   v
+-----------------------------------------------------------------------------------+
|                           API BACKEND (FastAPI - Python)                          |
|                                                                                   |
|  +--------------------+    +-----------------------+    +----------------------+  |
|  | Router & Auth      |--> | Data Engine (SQL)     |    | IA Engine (RAG)      |  |
|  +--------------------+    +-----------------------+    +----------------------+  |
|                               |               ^                |               |  |
+-------------------------------|---------------|----------------|---------------|--+
                                | SQL Queries   | JSON           | Vector Search |
                                v               |                v               |
+------------------+    +---------------+       |         +------------+         |
| ETL Pipelines    |--> | PostgreSQL    |       |         | ChromaDB   |         |
| (Python Scripts) |    | (Macro-Eco)   |---------------->| (Vectors)  |         |
+------------------+    +---------------+       |         +------------+         |
         ^                                      |                ^
         | CSV / API / Scraping                 |                | (Chunking/Embedding)
+------------------------------------------+    |         +------------+
|  Sources (World Bank, BRH, IHSI)         |    |         | PDF Parser |
+------------------------------------------+    v         +------------+
                                          +----------+           ^
                                          | LLM API  |<----------+ Textes BRH/FMI
                                          | (OpenAI) |
                                          +----------+
```

---

## 3. Flux Techniques Majeurs (Workflows)

### Flux A : Ingestion Périodique Documentaire (Pipeline Batch)
1. Le script `ingest_brh.py` télécharge le dernier PDF trimestriel.
2. `PyMuPDF` extrait le texte.
3. Le *Semantic Chunker* découpe le texte (ex: 500 tokens / chunk).
4. Ajout des Métadonnées Pydantic (source, date, page).
5. Appel API Endpoint OpenAI `text-embedding-3-small` pour vectoriser.
6. Insertion dans le Store ChromaDB local.

### Flux B : Requête Utilisateur ("Donne-moi le taux d'inflation de 2023 et explique pourquoi")
1. **Frontend :** Streamlit capture l'input et appelle le backend via un `POST /api/v1/query`.
2. **Backend Router (FastAPI) :** Identifie le besoin hybride via LLM (ou keyword matching pour le MVP).
3. **Appel 1 (SQL) :** FastAPI interroge PostgreSQL : `SELECT value FROM macro WHERE indicator='inflation' AND year=2023`.
4. **Appel 2 (RAG) :** FastAPI convertit la question en vecteur, appelle ChromaDB pour récupérer les 3 meilleurs chunks de 2023.
5. **Génération LLM :** FastAPI construit un prompt contenant a) les chunks RAG, b) le chiffre SQL. Il appelle l'API LLM (OpenAI) pour synthétiser la narration sourcée.
6. **Réponse :** FastAPI retourne au frontend un objet `ResponseModel` contenant : `{text: "...", source_links: [...], chart_data: [...] }`. Streamlit l'affiche interactivement.

---

## 4. Arbitrages Techniques et Compromis

| Décision | Compromis (Trade-off) | Bénéfice (Pourquoi ce choix ?) |
| :--- | :--- | :--- |
| **FastAPI vs Flask** | Courbe d'apprentissage asynchrone (async/await). | Modélisation Pydantic stricte, validation de la donnée (crucial en Data). API de perf supérieure. |
| **Chroma vs FAISS** | ChromaDB est légèrement plus lourd niveau dépendances que FAISS CPU. | Gère nativement la persistance et surtout le filtrage pré-recherche par métadonnées (Metadata Filtering) critique pour nos sources. |
| **Streamlit vs React** | Design moins personnalisable, un peu rigide sur l'UX complexe. | Division du TTM (Time to Market) par 4. Permet au développeur Backend/AI de tout faire en Python. |

---

## 5. Recommandation Finale & "Blueprint" du Répertoire MVP

L'architecture validée repose sur une approche API-First, mais empaquetée en monorepo piloté par Docker pour un déploiement simple, avec Streamlit comme interface MVP.

```bash
haiti-data-intelligence/
├── backend/                  # Application FastAPI
│   ├── api/                  # Endpoints (routes HTTP)
│   ├── core/                 # Config, Logging
│   ├── modules/
│   │   ├── data_engine/      # SQL Queries, SQLAlchemy Models
│   │   └── rag_engine/       # LlamaIndex/LangChain setup, Prompt Templates
│   └── database.py           # Connexion DB (Postgres/Chroma)
├── data_ingestion/           # Pipelines ETL standalones
│   ├── sql_loaders/          # Scripts d'update World Bank / BRH
│   └── document_loaders/     # Parsing PDF et injección Chroma
├── frontend_mvp/             # App Streamlit
│   ├── app.py                # Main Streamlit file
│   └── components/           # Widgets, Charts Plotly/Streamlit
├── tests/                    # Pytest
└── docker-compose.yml        # Orchestration (API + UI + Postgres + Chroma)
```
