# Checklist: Haiti Data Intelligence

## Phase 1 : Cadrage & Architecture (MVP)
- [x] 1.1 Validation de la roadmap par l'utilisateur
- [x] 1.2 Spécification des sources de données prioritaires (Macroéconomie, Rapports)
- [x] 1.2.1 Stratégie de sélection des sources (Matrice de qualité)
- [x] 1.2.2 Stratégie globale de traitement des données (Hybride RAG/SQL)
- [x] 1.2.3 Architecture Fonctionnelle (Blocs, Rôles, Flux)
- [x] 1.3 Choix détaillé de la stack technologique (Frontend, API, DBs, LLM)
- [x] 1.4 Création du plan d'implémentation detaillé (implementation_plan.md)

## Phase 2 : Data Engineering & Ingénierie des Connaissances
- [x] 2.0 Conception du schéma de base de données relationnelle
- [ ] 2.1 Setup de l'environnement de développement
- [x] 2.2 Conception globale de la stratégie d'ingestion ETL
- [ ] 2.3 Création et peuplement de la base de données relationnelle
- [ ] 2.4 Création et peuplement de la base de données vectorielle (Documents)

## Phase 3 : Intelligence Artificielle & IA Générative
- [ ] 3.1 Implémentation du Retriever hybride (Documents)
- [ ] 3.2 Implémentation de la chaîne RAG avec génération sourcée
- [ ] 3.3 Implémentation de l'Agent d'analyse de données structurées (Text-to-SQL)

## Phase 4 : Architecture Backend
- [ ] 4.1 Développement des endpoints d'API Data (Graphiques, Métriques)
- [ ] 4.2 Développement des endpoints d'API IA (Chat, Requêtes)
- [ ] 4.3 Génération dynamique d'exports (PDFs)

## Phase 5 : Frontend & Interface Utilisateur
- [ ] 5.1 Initialisation du projet Frontend
- [ ] 5.2 Création des Dashboard macroéconomiques et comparateur de pays
- [ ] 5.3 Intégration de l'interface conversationnelle (ChatBot) avec retour des sources

## Phase 6 : Tests & Déploiement Cloud
- [ ] 6.1 Tests d'intégration RAG et Data
- [ ] 6.2 Dockerisation du Backend et Frontend
- [ ] 6.3 Configuration CI/CD
- [ ] 6.4 Déploiement en production (AWS/GCP/Vercel/Render)
