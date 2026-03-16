# Roadmap: Haiti Data Intelligence

## Vision du Produit
Une plateforme professionnelle d’intelligence socio-économique sur Haïti permettant :
- La recherche hybride (RAG) sur des documents officiels et rapports qualitatifs.
- L'analyse de données structurées macroéconomiques avec comparaison inter-pays.
- La génération automatique de graphiques (Data Visualization) et de briefings sources.

---

## Phase 1 : Cadrage & Architecture (MVP)
**Objectifs :** Définir le périmètre exact, les sources de données et valider l'architecture technique de base.
- [ ] Identifier et catégoriser les sources de données (ex: rapports de la BRH, IHSI, Banque Mondiale, FMI).
- [ ] Fixer la pile technologique (Frontend, Backend, Base de données relationnelle, Vector Store, LLM Provider).
- [ ] Établir l'architecture logicielle modulaire (Séparation des préoccupations).
**Livrable attendu :** *implementation_plan.md* (Cahier des charges technique et architecture logicielle).

## Phase 2 : Data Engineering & Ingénierie des Connaissances
**Objectifs :** Collecter, nettoyer et préparer les données pour qu'elles soient prêtes à être ingérées par l'IA.
- [ ] Développer les scripts d'extraction (Scraping, APIs) pour les données d'Haïti et d'autres pays cibles.
- [ ] Mettre en place un entrepôt de données relationnel (ex: SQLite pour le MVP, PostgreSQL pour la prod).
- [ ] Mettre en place le pipeline d'ingestion documentaire (lecture PDF/Word, nettoyage, chunking sémantique, embedding) vers une base vectorielle (ex: FAISS, Qdrant, Chroma).
**Livrables attendus :** Base de données macroéconomique structurée, Vector Store documenté, Scripts ETL fonctionnels.

## Phase 3 : Intelligence Artificielle (RAG & Analyse Sémantique)
**Objectifs :** Développer le "cerveau" capable d'interroger les deux types de données.
- [ ] Implémenter le moteur de recherche documentaire hybride (Retriever).
- [ ] Mettre au point un chaînage LLM performant pour la génération d'une réponse avec citations exactes (RAG).
- [ ] Intégrer un Agent cognitif ou Text-to-SQL (ex: PandasAI / LangChain SQL Agent) pour interroger les données structurées et générer des statistiques.
**Livrables attendus :** Module Python/IA central testable indépendamment des interfaces.

## Phase 4 : Développement API Backend
**Objectifs :** Exposer les capacités de données et d'IA de manière sécurisée et robuste.
- [ ] Construire les API (ex: FastAPI) exposant les services (Recherche RAG, Requête Data Structurée, Exports).
- [ ] Structurer la logique métier et la gestion des sessions/historiques de requêtes.
- [ ] Mise en place de la génération dynamique de fichiers (PDFs de briefing).
**Livrable attendu :** API REST documentée (Swagger) prête à être consommée par le Frontend.

## Phase 5 : Développement Frontend & UI/UX
**Objectifs :** Créer une interface utilisateur professionnelle, fluide et impactante.
- [ ] Créer l'application Web moderne (React/Next.js ou éventuellement Streamlit avancé pour l'itération rapide MVP).
- [ ] Développer l'interface de Data-Visualization : Tableaux de bord dynamiques et comparateurs (Recharts, Plotly).
- [ ] Développer l'interface conversationnelle orientée "Analyste" (Chat, sources cliquables, feedback).
**Livrables attendus :** Interface Web complète, responsive et connectée à l'API.

## Phase 6 : Assurance Qualité (QA) & Optimisation
**Objectifs :** Fiabiliser les réponses et le système.
- [ ] Implémenter des tests unitaires et d'intégration sur les composants critiques.
- [ ] Évaluation du RAG (métriques de fidélité, pertinence et biais) via des frameworks (ex: Ragas).
- [ ] Correction des prompts et optimisation de la vitesse des requêtes.
**Livrable attendu :** Rapports de tests, Codebase stabilisée.

## Phase 7 : DevOps & Déploiement
**Objectifs :** Rendre la plateforme accessible, sécurisée et "production-ready".
- [ ] Conteneurisation totale de l'application (Docker, docker-compose).
- [ ] Configuration des pipelines CI/CD (GitHub Actions).
- [ ] Déploiement sur une infrastructure Cloud (AWS, GCP, ou combo Vercel / Render / Supabase).
**Livrable attendu :** Plateforme accessible publiquement, Monitoring des requêtes et des coûts LLM.
