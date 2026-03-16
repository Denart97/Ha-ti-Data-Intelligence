# Définition du MVP : Haiti Data Intelligence

Ce document définit précisément le périmètre du Produit Minimum Viable (MVP) pour la plateforme "Haiti Data Intelligence", ainsi que la feuille de route pour les versions ultérieures (V2 et V3/Exclusions au démarrage). L'approche privilégie un livrable réaliste, démontrant immédiatement de la valeur et techniquement réalisable rapidement pour tester le marché.

---

## 1. Fonctionnalités MVP (Indispensable)
Ces fonctionnalités constituent le noyau dur ("Core") servant à prouver la pertinence de la proposition de valeur.

- **Recherche Documentaire Sourcée (RAG Core) :**
  - Indexation d'un corpus limité et très qualitatif : Rapports trimestriels de la BRH (2020-2026) et les rapports récents de la Banque Mondiale/FMI sur Haïti (2020-2026).
  - Interface de Chat conversationnelle (Q/R) permettant d'interroger ces documents.
  - Fonctionnalité de citation stricte : chaque réponse doit s'accompagner d'un lien (ou d'une référence page/paragraphe) vers le document PDF source.
- **Tableau de Bord Macroéconomique (Data Core) :**
  - Base de données structurée limitée à 5 à 10 indicateurs clés (PIB, Inflation, Taux de Change HTG/USD, Taux Directeur, Réserves Internationales, Import/Export).
  - Visualisations interactives (Courbes, Histogrammes) pour ces 10 indicateurs sur un historique de 10 ans.
  - Fonctionnalité simple de filtre par année et par indicateur.
- **Comparaison Basique (Benchmark) :**
  - Capacité de superposer sur les graphiques macroéconomiques les données de deux pays comparables pré-sélectionnés (ex: République Dominicaine, Jamaïque), provenant de bases internationales fiables (World Bank Open Data).
- **Interface Utilisateur :**
  - Une application web SPA (Single Page Application) avec deux onglets principaux : "Dashboard Data" et "Assistant IA (RAG)".

## 2. Fonctionnalités V2 (Utile mais peut attendre)
Des fonctionnalités à forte valeur ajoutée, mais qui nécessitent trop d'ingénierie fine ou présentent un risque pour un premier lancement.

- **Agent Sémantique Data (Text-to-SQL) :** Poser des questions en langage naturel pour interroger la base de données relationnelle ("Quelle a été l'inflation moyenne entre 2015 et 2020 ?") et générer un graphique à la volée.
- **Génération Automatique de Rapports (Briefings) :** Un clic pour générer un PDF de synthèse combinant les graphiques actuels et des analyses textuelles issues du RAG.
- **Historique et Sessions Utilisateur :** Authentification basique (Login/Password), sauvegarde des conversations précédentes, personnalisation des graphiques favoris.
- **Élargissement Sémantique :** Intégration de documents supplémentaires moins structurés (Articles de presse spécialisée type Le Nouvelliste Eco, discours, notes de conjoncture IHSI complètes).
- **Alertes et Notifications :** Envoi d'un email automatisé lors de l'intégration d'un nouveau rapport.

## 3. Fonctionnalités V3 & Exclusions au démarrage
Ce qui doit absolument être reporté pour éviter l'éparpillement ("Scope Creep").

- **Scraping Automatisé en Temps Réel :** Des robots complexes allant récupérer les données quotidiennes sur des sites peu structurés. Pour le MVP, les données seront chargées statiquement ou via des scripts ETL semi-manuels déclenchés par cron.
- **Interface Multilingue complète :** Le MVP et les données seront dans la langue principale des affaires locale/internationale (Français et optionnellement Anglais). Le Créole attendra une V3 en raison de la complexité des modèles de langage sur cette langue.
- **Modèles LLM fine-tunés en local :** Le MVP s'appuiera sur des API cloud robustes (ex: OpenAI GPT-4o ou Anthropic Claude 3) pour la fiabilité et la rapidité. L'hébergement de LLMs locaux sécurisés (Llama 3) est une optimisation de coûts/sécurité pour plus tard.
- **Paiements et Billing avancés :** L'intégration de Stripe pour des abonnements granulaires. Le MVP pourra fonctionner sur un accès "Freemium ouvert" ou "Bêta sur invitation" non facturée automatiquement.

---

## 4. Justifications des choix du MVP

| Choix | Justification (Risque / Valeur) |
| :--- | :--- |
| **Limitation à 10 indicateurs macro (MVP)** | Réduit le temps d'ingénierie Data (ETL, nettoyage des valeurs nulles). Démontre instantanément la valeur du Dashboard sans noyer l'utilisateur. |
| **RAG limité BRH/Banque Mondiale (MVP)** | Ces sources sont denses et textuelles (la résolution d'un vrai "pain point" d'analyste). Évite de passer des semaines à nettoyer des PDFs mal formés de sources moins régulières. |
| **Citation obligatoire des sources (MVP)** | Indispensable pour la crédibilité (B2B/B2Institution). Un système "boîte noire" (où l'IA répond sans preuve) échouera sur ce marché soucieux de la véracité. |
| **Exclusion de Text-to-SQL du MVP** | Le Text-to-SQL pur nécessite du prompting complexe et tend à halluciner sur des schémas de données compliqués. Un Dashboard pré-défini est plus robuste pour une V1. |
| **Scripts ETL simples vs Scraping Complexe** | L'objectif du MVP est de montrer la *consommation* de la donnée, pas la prouesse technique de *récupération*. Des chargements de CSV/APIs propres initiales suffisent pour la démo. |

---

## 5. Scénario de Démonstration (Le "Pitch" MVP)

Voici comment se déroulera une démo du MVP devant un prospect (ex: un Directeur de Banque ou représentant d'ONG) :

1. **L'Accroche :**
   * *L'utilisateur (Vous)* : "Bienvenue sur Haiti Data Intelligence. Vous cherchez à préparer une note sur l'environnement monétaire par rapport à nos voisins, et de comprendre la réaction de la Banque Centrale."
2. **Phase 1 (Le Dashboard Quantitatif) :**
   * *Action* : Vous ouvrez l'onglet "Dashboard".
   * *Vue* : Un panneau fluide s'affiche avec la courbe de l'inflation haïtienne depuis 2015.
   * *Action* : En deux clics, vous ajoutez la République Dominicaine sur le même graphique.
   * *Résultat* : La comparaison est immédiate, visuelle et le graphique peut être exporté en PNG. "Plus besoin d'aller fouiller sur trois sites différents ou faire vos Vlookup Excel."
3. **Phase 2 (Le Moteur IA RAG - Qualitatif) :**
   * *Action* : Vous basculez sur l'onglet "Assistant".
   * *Prompt tapé* : `"Quels sont les facteurs ayant influencé l'inflation en 2023 selon la BRH ?"`
   * *Résultat* : En 3 secondes, l'IA génère un paragraphe synthétique résumant les facteurs conjoncturels ou monétaires.
   * **Le moment "Wahou"** : Sous le paragraphe, un bouton cliquable apparaît : `Source: Note sur la Politique Monétaire (T3 2023) - Page 4`. En cliquant, le PDF original s'ouvre exactement sur le paragraphe cité, confirmant l'information.
4. **La Conclusion :**
   * "Vous venez de faire une analyse combinée quantitative inter-pays et une revue documentaire qualifiée en moins d'une minute."
