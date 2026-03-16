# Cadrage Métier : Haiti Data Intelligence

## Résumé Exécutif
Haiti Data Intelligence est une plateforme B2B et B2Institution visant à démocratiser, fiabiliser et accélérer l'accès aux données socio-économiques haïtiennes. Ce projet répond à un déficit d'information structurée qui ralentit les prises de décisions des investisseurs, bailleurs de fonds, chercheurs et décideurs publics. En combinant l'analyse de données macroéconomiques classiques à une IA générative (RAG) interrogeant des documents qualitatifs, la plateforme offre un avantage comparatif inédit : une veille sourcée, immédiate et facilement actionnable. Le MVP vise à valider cette proposition de valeur en se concentrant sur les indicateurs financiers et rapports institutionnels critiques (ex: BRH, IHSI).

---

## Analyse Métier

### 1. Le problème résolu
Le marché haïtien souffre d'un paradoxe de l'information : les données (macroéconomiques, sociales, sectorielles) existent mais sont :
- **Fragmentées** : dispersées entre multiples ministères, banques centrales (BRH), instituts statistiques (IHSI), et ONG.
- **Peu exploitables** : souvent bloquées dans de longs rapports PDF non structurés.
- **Difficiles à contextualiser** : difficile de comparer instantanément la situation d'Haïti avec celle de pays aux dynamiques similaires (ex: République Dominicaine, pays de la CARICOM) sans fastidieux travaux manuels.
- **Non-Standardisées** : l'absence d'une API unifiée rend difficile l'intégration des données dans les modèles analytiques modernes.

### 2. La proposition de valeur
« **Transformer le chaos informationnel haïtien en intelligence économique actionnable, en quelques secondes.** »
- **Pour l'analyste** : Gain de temps massif grâce à un moteur RAG qui "lit" et synthétise les rapports officiels.
- **Pour le décideur** : Tableaux de bord macroéconomiques "prêts à l'emploi" pour des comparaisons inter-pays et des visualisations claires.
- **Pour l'organisation** : Fiabilité accrue avec des systèmes de réponses sourcées ("grounded" sur des sources officielles) pour réduire le risque d'hallucination IA.

### 3. Segments clients cibles
1. **Secteur Financier & Investisseurs** : Banques commerciales haïtiennes, fonds d’investissement multilatéraux (SFI, BID), analystes risque-pays.
2. **Décideurs Publics & ONG** : Bailleurs de fonds (Banque Mondiale, USAID, FMI), ministères haïtiens, ONG de développement cherchant à valider l'impact de leurs interventions.
3. **Monde Académique & Médias** : Chercheurs en économie du développement, journalistes d'investigation spécialisés, think tanks.

---

## Tableau des Personas Prioritaires

| Nom & Rôle | Objectifs Principaux | Frustrations Actuelles | Bénéfices Attendus (HDI) |
| :--- | :--- | :--- | :--- |
| **Marc, Analyste Risque-Pays (Expatrié)** | Évaluer la viabilité d'investissements, produire des rapports trimestriels pour son siège. | Perd 60% de son temps à chercher les derniers chiffres de l'inflation de l'IHSI et les bulletins de la BRH. | Accès API aux données à jour. Graphiques pré-calculés. Recherches sémantiques ciblées dans les rapports. |
| **Sophia, Cadre dirigeante en Banque Locale** | Suivre l'évolution du taux de change, de la liquidité et faire du benchmarking régional. | Les données sont livrées en PDF, l'export Excel est manuel et prône aux erreurs. | Dashboard interactif pour surveiller en temps-réel sa position face à l'environnement macroéconomique local et régional. |
| **Jean, Économiste / Chercheur Universitaire** | Modéliser l'impact des politiques monétaires en Haïti comparé à d'autres économies insulaires. | Absence de séries temporelles longues et "propres" (sans valeurs manquantes). | Base de données relationnelle propre, interrogeable via des Agents IA (Text-to-SQL) pour obtenir des tendances historiques vite. |

---

## Tableau des Cas d'Usage Principaux

| Cas d'Usage | Description | Interactions Utilisateur | Technologies Sous-jacentes Cibles |
| :--- | :--- | :--- | :--- |
| **CU1: Q/R Documentaire (RAG)** | Poser une question sur un rapport précis (ex: "Quelles sont les prévisions d'inflation selon le dernier rapport FMI sur Haïti ?"). | Chatbot. L'utilisateur pose sa question, le système répond avec la section du PDF citée en source. | Vector Database, Pipeline Ingestion PDF, LLM, LangChain/LlamaIndex. |
| **CU2: Benchmark Macroéconomique** | Comparer le PIB, le taux de chômage ou l'inflation d'Haïti avec le Costa Rica et la République Dominicaine. | Sélection de pays et d'indicateurs via des menus déroulants. Affichage de graphiques superposés. | Base relationnelle (PostgreSQL etc.), API REST, Frontend Chart (Recharts / Plotly). |
| **CU3: Génération de Briefing** | Produire une note de synthèse d'une page sur la situation monétaire actuelle pour un COMEX. | Clic sur un bouton "Générer Rapport Monétaire". | LLM (mise en forme), Agents IA (assemblage Data + Texte RAG), Générateur PDF. |
| **CU4: Requête Data Sémantique** | Permettre à un non-codeur d'interroger la base : "Montre-moi l'évolution des réserves de change de la BRH depuis 2010". | Interface de prompt "Data". Affiche directement un tableau dynamique ou un graphique en sortie. | Agent Text-To-SQL ou Data Analysis (ex: PandasAI). |

---

## Analyse Stratégique

### 1. Risques Métier & Mitigations
- **Fiabilité / Fraîcheur des sources :** Les institutions haïtiennes peuvent publier avec retard ou de manière irrégulière.
  * *Mitigation :* Indiquer clairement la date de dernière mise à jour. Créer des alertes pour le scraper dès la publication de documents officiels. Travailler sur les bases internationales (Banque Mondiale) pour combler les trous.
- **Hallucinations de l'IA (Risque Critique en FinTech/Eco) :**
  * *Mitigation :* Restreindre le LLM via un prompt drastique : s'il ne trouve pas la réponse dans le contexte (RAG), il doit répondre "Donnée non trouvée". Forcer l'affichage du lien PDF original en citation.

### 2. Opportunités de Monétisation
- **Freemium :** Accès gratuit aux séries macroéconomiques de base et dashboard limités (modèle "Trading Economics").
- **Abonnement Pro (SaaS B2B) :** Accès illimité au moteur de recherche RAG sur tous les rapports officiels, export PDF/Excel, alertes sur les nouveaux rapports, comparaison multi-pays avancée.
- **Licence Entreprise (API Access) :** Accès complet à l'API Data et à l'infrastructure d'embeddings documentaire pour intégration dans les SI des banques.

### 3. Indicateurs de Succès (KPIs)
- **Acquisition :** Nombre d'utilisateurs inscrits (Tier gratuit) au bout de 3 mois.
- **Engagement :** Nombre de requêtes RAG ou de requêtes API exécutées par semaine par utilisateur (DAU/MAU).
- **Rétention / Valeur :** Taux de conversion Freemium -> Pro.
- **Qualité IA :** Taux de feedback positif (pouce levé/baissé) sur les réponses du RAG.

---

## Conclusion et Recommandation MVP
Le marché nécessite une solution combinant *Insights* qualitatifs et quantitatifs.
Pour le **Minimum Viable Product (MVP)**, il est recommandé de **ne pas chercher à scrapper toutes les sources dès le jour 1**, mais de se restreindre à la portée suivante (Le "Core Scope") :
1. **Données Qualitatives (RAG)** : Indexation limitée aux publications de la Banque de la République d'Haïti (BRH) des 3 dernières années, et des rapports trimestriels clés de la Banque Mondiale/FMI pour Haïti.
2. **Données Quantitatives (DB)** : 5 à 10 séries macroéconomiques principales (PIB, Inflation, Change, Taux directeur, Réserves), sur les 10 dernières années. Comparatif avec 2 autres pays (ex: RD et Jamaique).
3. **Interface** : Un dashboard combiné avec une barre de recherche "Chat" hybride (capable de répondre aussi bien par un texte que par un mini-graphique).
