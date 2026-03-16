# Architecture Fonctionnelle : Haiti Data Intelligence

Ce document modélise le système en "boîtes noires" fonctionnelles. Il décrit ce que fait chaque composant majeur de la plateforme, quelles données il ingère et ce qu'il produit, indépendamment des technologies qui seront choisies.

---

## 1. Schéma Fonctionnel Textuel (Data Flow)

```text
[ Sources Externes (BRH, IHSI, PDF, APIs) ] 
       │
       ▼
[ 1. Ingestion (Scrapers, ETL, PDF Parsers) ] ──▶ [ 10. Gestion des Sources (Audit, Qualité) ]
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[ 3. Enrichissement (Metadata) ]   [ 3. Enrichissement (Chunking, Embedding) ]
       │                                 │
       ▼                                 ▼
[ 2. Stockage (Base SQL) ]         [ 2. Stockage (Base Vectorielle) ]
       │                                 │
       │           ┌─────────────────────┘
       │           │
       ▼           ▼
[ 6. Moteur de Routage (LLM Router) ] ◀── [ Requête Utilisateur UI ]
       │           │
       │           ├────────────────────────────┐
       ▼           ▼                            ▼
[ 4. Moteur   ]  [ 5. Moteur RAG ]        [ 9. Génération ]
[ Analytique  ]  [ (Recherche Sém) ]      [ de Briefs   ]
       │           │                            │
       ▼           ▼                            ▼
[ 7. Génération de Réponses (Orchestration LLM + Synthèse) ]
       │
       ▼
[ 8. Visualisation (Dashboard UI) ] ──▶ [ Utilisateur Final ]

* En arrière-plan : [ 11. Journalisation ] et [ 12. Monitoring ] surveillent l'ensemble.
```

---

## 2. Description des Blocs Fonctionnels

### 1. Bloc Ingestion (Extract, Load)
- **Rôle :** Collecter la donnée brute depuis le monde extérieur. Gère le téléchargement des CSV, la connexion aux APIs internationales (WB), et le téléchargement des PDF institutionnels.
- **Entrées :** URLs, APIs REST (Banque Mondiale), Fichiers PDF/Excel locaux.
- **Sorties :** Fichiers bruts standardisés stockés temporairement (ex: un DataFrame plat ou un texte brut extrait d'un PDF).
- **Dépendances :** Internet, Indisponibilité des sites sources (BRH/IHSI).
- **Criticité :** **Haute**. C'est le point d'entrée. Si l'ingestion casse en silence, la plateforme devient obsolète.

### 2. Bloc Stockage (Data Warehouse & Vector Store)
- **Rôle :** Persister les données de manière optimale pour y accéder rapidement. Séparé en deux sous-systèmes (Relationnel pour les chiffres, Vectoriel pour les embeddings textuels).
- **Entrées :** Données enrichies prêtes à l'emploi, Textes vectorisés.
- **Sorties :** Résultats de requêtes SQL (JSON), "Chunks" de texte pertinents via recherche de similarité.
- **Dépendances :** Bloc Ingestion, Bloc Enrichissement.
- **Criticité :** **Critique**. Perte de données = arrêt du service.

### 3. Bloc Enrichissement (Transform & Embedding)
- **Rôle :** Nettoyer et transformer la donnée brute. Pour les chiffres : gérer les valeurs nulles, standardiser les dates. Pour les textes : découper le texte (Chunking), appliquer la taxonomie métier (Metadata tagging) et convertir le texte en vecteurs (Embedding).
- **Entrées :** Données brutes issues de l'ingestion, Taxonomie (dictionnaire métier).
- **Sorties :** Textes segmentés et vectorisés avec citations (Metadata), Tables de faits macroéconomiques propres.
- **Dépendances :** Modèle d'Embedding LLM.
- **Criticité :** **Haute**. Une mauvaise qualité d'enrichissement (mauvais découpage de PDF) ruine la qualité des réponses de l'IA.

### 4. Moteur Analytique (SQL Engine)
- **Rôle :** Exécuter les calculs statistiques et requêter les séries temporelles pour le Dashboard.
- **Entrées :** Requête API formatée ou requête Text-to-SQL issue du routeur.
- **Sorties :** Listes de tableaux interactifs, Séries temporelles (X: Dates, Y: Valeurs).
- **Dépendances :** Stockage SQL.
- **Criticité :** **Moyenne/Haute**. (Le Dashboard s'affiche plus).

### 5. Moteur RAG (Recherche Documentaire)
- **Rôle :** Retrouver les paragraphes originaux pertinents par rapport à la question posée, en utilisant une recherche sémantique hybride (vecteur + mot-clé).
- **Entrées :** Question de l'utilisateur (vectorisée).
- **Sorties :** Top-K chunks de texte (ex: les 5 meilleurs paragraphes) avec leurs URL de source et numéros de page.
- **Dépendances :** Stockage Vectoriel, Modèle d'Embedding.
- **Criticité :** **Critique** pour l'onglet Assistant.

### 6. Moteur de Routage (Intent Classifier)
- **Rôle :** Le chef d'orchestre en entrée. Il lit la question en langage naturel et détermine quelle base interroger (Data ou RAG ou les deux).
- **Entrées :** Requête brute en langage naturel.
- **Sorties :** Ordre d'exécution ("Go SQL", "Go Vector", ou "Go Hybrid").
- **Dépendances :** LLM rapide (faible latence) et prompt de classification ("Few-shot prompting").
- **Criticité :** **Moyenne**. S'il se trompe, il cherchera du texte quand l'utilisateur voulait un chiffre, générant une frustration UI.

### 7. Génération de Réponses (LLM Synthesizer)
- **Rôle :** Formuler la réponse textuelle finale adressée à l'utilisateur. Il lit les fragments trouvés par le RAG, les synthétise de manière professionnelle et ajoute les balises de citation. Applique les règles anti-hallucination.
- **Entrées :** Contexte récupéré (Chunks textuels + Données graphiques JSON), Question d'origine.
- **Sorties :** Texte structuré (Markdown), prêt à être affiché avec citations.
- **Dépendances :** Moteur RAG, Moteur Analytique, LLM Provider (ex: OpenAI GPT-4o).
- **Criticité :** **Critique**. Si le LLM tombe, le chat n'existe plus.

### 8. Visualisation (UI / Dashboard)
- **Rôle :** L'interface client. Afficher des graphiques (Courbes, Barres) comparatifs et l'interface de messagerie textuelle de manière fluide.
- **Entrées :** JSON du Moteur Analytique, Markdown du Moteur de Génération.
- **Sorties :** Interface Web. Intéractions clics de l'utilisateur.
- **Dépendances :** Framework Frontend (ex: Next.js), Librairie de Charts.
- **Criticité :** **Haute** (Expérience Utilisateur).

### 9. Génération de Briefs (Reporting Automation)
- **Rôle :** Compiler des tableaux, des textes RAG et des graphiques statiques dans un document PDF ou Word téléchargeable (One-Pager).
- **Entrées :** Commande de l'UI, Réponse Générée générique, JSON Analytique.
- **Sorties :** Fichier PDF.
- **Dépendances :** Générateur PDF backend (ex: Puppeteer, ReportLab).
- **Criticité :** **Faible** (Cas d'usage V2 asynchrone, optionnel pour le cœur du MVP).

### 10. Gestion des Sources (Master Data Management)
- **Rôle :** Gérer le cycle de vie de la source. Module Admin permettant de cocher/décocher une source, surveiller l'état des extracteurs (Scrapers), et résoudre les conflits d'informations.
- **Entrées :** Config de la gouvernance (cf `strategie_sources.md`), Métadonnées d'ingestion.
- **Sorties :** Logs de qualité de données, Dashboard Admin.
- **Dépendances :** -
- **Criticité :** **Faible** pour l'utilisateur final, **Haute** pour le Data Engineer interne.

### 11. Journalisation (Event Logging)
- **Rôle :** Stocker "Qui a fait quoi, quand ?". Trace d'audit de sécurité et de debugging technique.
- **Entrées :** Logs serveurs, Traces d'erreurs, Horodatage des ingestions.
- **Sorties :** Fichiers textes structurés (ex: JSON Lines).
- **Dépendances :** Infrastucture (ex: ELK Stack, ou simple Log file).
- **Criticité :** **Moyenne**.

### 12. Monitoring (LLMOps)
- **Rôle :** Surveiller la performance spécifique de l'IA et de l'Infra. Temps de réponse, nombre de requêtes SQL lentes, et surtout : Comptage des "Tokens" LLM pour maîtriser la facturation API ($).
- **Entrées :** Traces du Router et de la Génération (Latence, Tokens consommés, Coût estimé).
- **Sorties :** Alertes (Email/Slack si coût > plafond), Dashboard DevOps.
- **Dépendances :** Framework LLMOps (ex: LangSmith, Arize Phoenix).
- **Criticité :** **Haute** financièrement. Un LLM en boucle peut générer une facture imprévue majeure.
