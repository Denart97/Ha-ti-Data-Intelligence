# Plan d'Implémentation : Architecture & Arborescence

Ce document présente l'organisation physique du code ("Repository Structure") pour le projet Haiti Data Intelligence. Cette arborescence est conçue pour être modulaire, facilitant un développement MVP rapide sous Python/Streamlit tout en préparant la voie pour une scalabilité future (V2 sous Next.js/Docker-Compose complexe).

## Arborescence Complète du Repository

```text
haiti-data-intelligence/
│
├── data_ingestion/          # 1. Pipeline d'Acquisition (ETL)
│   ├── sql_loaders/         # Scripts d'extraction des données structurées
│   │   ├── wb_api_fetch.py  # Tire Data via API World Bank
│   │   └── brh_scraper.py   # Scrape les Excels/CSV de la BRH
│   ├── pdf_loaders/         # Scripts d'extraction documentaire
│   │   ├── brh_pdf_fetch.py # Téléchargement & Parsing PDFs institutionnels
│   │   └── fmi_pdf_fetch.py
│   └── cron_jobs.yaml       # Planification des jobs de mise à jour (Ex: GitHub Actions)
│
├── backend/                 # 2. Cœur Serveur & API (FastAPI)
│   ├── api/                 # Contrôleurs HTTP de l'API REST
│   │   ├── routers/
│   │   │   ├── chat.py      # Endpoints pour le RAG conversationnel (POST /chat)
│   │   │   └── macro.py     # Endpoints de données statistiques (GET /macro/inflation)
│   │   └── main.py          # Point d'entrée de l'API FastAPI
│   ├── core/                # Configuration transversale du Backend
│   │   ├── config.py        # Settings Pydantic (Variables d'environnement)
│   │   ├── security.py      # Authentification (JWT, API Keys)
│   │   └── exceptions.py    # Gestion d'erreurs globales
│   ├── db/                  # Gestion des Connexions aux Bases de données
│   │   ├── pg_session.py    # Setup SQLAlchemy / PostgreSQL
│   │   └── vector_store.py  # Setup Client ChromaDB
│   ├── models/              # Modèles de Données (ORM & Pydantic)
│   │   ├── sql_models.py    # Schémas PostgreSQL (Séries temporelles)
│   │   └── schemas.py       # Pydantic (Validation In/Out des APIs)
│   └── services/            # Logique Métier (Le "Cerveau")
│       ├── analytics/       # 3. Moteur Analytique (SQL/Data)
│       │   └── stats_calc.py# Agrégations, calculs glissants, requêtes DB complexes
│       ├── rag/             # 4. Moteur RAG & NLP
│       │   ├── retriever.py # Recherche vectorielle + Metadata filtering
│       │   ├── generator.py # Assemblage du contexte, LLM Prompts et anti-hallucination
│       │   └── indexer.py   # Logique d'embedding et chunking pour ChromaDB
│       └── router/          # 5. Moteur de Routage (Intent)
│           └── classifier.py# Détermine si la question -> RAG, SQL ou Hybride
│
├── frontend/                # 6. Interface Utilisateur (MVP Streamlit)
│   ├── app.py               # Point d'entrée Streamlit (Menu principal)
│   ├── pages/               # Vues de l'application
│   │   ├── 1_dashboard.py   # Vue des graphiques macroéconomiques (Data Structurées)
│   │   └── 2_assistant.py   # Vue du Chatbot RAG sourcé (Documents)
│   ├── components/          # Composants UI réutilisables
│   │   ├── charts.py        # Graphiques (Plotly)
│   │   ├── chat_bubble.py   # Bulle de réponse du RAG avec bouton source
│   │   └── filters.py       # Menus déroulants (Années, Pays)
│   └── utils/               # Helpers Frontend
│       └── api_client.py    # Fonctions appelant le "backend/api" (Requests)
│
├── data/                    # 7. Stockage local (Dev/MVP uniquement)
│   ├── raw/                 # Fichiers bruts déposés avant ETL (PDFs originaux)
│   ├── processed/           # CSV nettoyés (pour load dans PG)
│   └── chroma_db/           # Base Vectorielle locale (Dossier généré par Chroma)
│
├── scripts/                 # 8. Utilitaires d'administration 
│   ├── migrate_db.py        # Création des tables SQL (Alembic)
│   ├── seed_database.py     # Peuple la BDD avec les séries WorldBank de base
│   └── eval_rag.py          # Script d'évaluation de la qualité du RAG (Ragas métriques)
│
├── tests/                   # 9. Pipeline de Tests Automatisés
│   ├── conftest.py          # Fixtures Pytest (Fausses DB, Mock LLM)
│   ├── test_ingestion/      # Vérifie que les PDF sont bien lus
│   ├── test_backend/        # Tests des routes API (Statut 200, JSON valide)
│   ├── test_rag/            # Tests des prompts (Vérif anti-hallucination sur cas connus)
│   └── test_frontend/       # Tests e2e UI métiers
│
├── docs/                    # 10. Documentation
│   ├── architecture.md      # Schémas et décisions architecturales
│   ├── data_dictionary.md   # Lexique des variables (PIB, IPC...)
│   └── api_reference.md     # Exports Swagger / Redoc statiques
│
├── .env.example             # Template des clés secrètes (OPENAI_API_KEY, DB_URL)
├── .gitignore               # Exclut `data/`, `__pycache__`, et `.env`
├── docker-compose.yml       # Orchestre Postgres + Chroma + Backend + Frontend
├── Dockerfile.backend       # Image Docker pour FastAPI
├── Dockerfile.frontend      # Image Docker pour Streamlit
├── pyproject.toml           # Gestionnaire de dépendances Python (Poetry/uv)
└── README.md                # Guide de lancement du projet (Run MVP)
```

---

## Détails des Interactions Fonctionnelles

### L'axe `data_ingestion/` -> `backend/db/`
*   **Rôle :** Séparer physiquement les longs scripts de scraping des APIs en temps réel.
*   **Flux :** Les modules `data_ingestion` sont exécutés par des `cron_jobs` (ou scripts Python isolés). Ils récupèrent la data, utilisent `backend/services/rag/indexer.py` pour traiter les PDF, et écrivent les résultats directement dans `PostgreSQL` ou `ChromaDB`.

### L'axe `backend/api/` <-> `backend/services/`
*   **Rôle :** Séparation des préoccupations (MVC). `api` ne gère que les protocoles HTTP (Statuts 200, 404), la validation et l'authentification. Toute la logique complexe (Calculs DataFrame, Prompts LLM, Recherche Chroma) réside dans `services/`.
*   **Flux :** Un routeur `chat.py` intercepte une question, et la délègue à `services.router.classifier.py`.

### L'axe `frontend/` -> `backend/`
*   **Rôle :** Découplage strict entre Interface et Moteur. Streamlit ne fait aucune requête directe à la base de données.
*   **Flux :** Le `frontend/utils/api_client.py` envoie des requêtes HTTP REST au `backend/api`. Ainsi, si la V2 passe sur React ou si une banque demande l'accès API, le Backend n'a pas besoin de changer d'une seule ligne.

### Les dossiers cachés (`data/`, `tests/`, `scripts/`)
*   Le dossier `data/` sert uniquement au développement local (stockage des PDF téléchargés et du fichier SQLite/Chroma). En production, ce dossier est ignoré (volumes Docker, S3).
*   `scripts/` contient la maintenance (migrations, "seeding" de la première base).
*   **Criticité des tests :** Le module `tests/test_rag/` est vital. Il stockera des questions connues (Ground Truth) pour vérifier, par exemple, qu'un changement de modèle (Anthropic vs OpenAI) n'altère pas la fiabilité des réponses sur le "Financement monétaire" [Anti-Régression].
