# Cadrage Data : Haiti Data Intelligence

Ce document définit l'architecture de l'information cible pour la plateforme "Haiti Data Intelligence". Il structure les besoins en données par grandes familles thématiques (structurées et non structurées), en précisant pour chacune les caractéristiques clés d'un point de vue Produit.

---

## 1. Données Structurées (Dashboard & API Data)

### 1.1 Macroéconomie
- **Objectif métier :** Évaluer la santé économique globale du pays, la croissance et les grands équilibres financiers.
- **Type de données attendu :** Séries temporelles numériques (PIB, Croissance, Taux de change HTG/USD, Réserves internationales, Balance commerciale).
- **Niveau géographique pertinent :** National, Comparatif international (CARICOM, Rép. Dominicaine).
- **Fréquence :** Mensuelle (Change, Réserves) à Annuelle (PIB).
- **Difficultés potentielles :** Révisions fréquentes des chiffres du PIB par l'IHSI ; décalage entre les années fiscales haïtiennes (oct-sept) et civiles internationales.
- **Valeur ajoutée pour le produit :** Constitue le "Core Data" de la plateforme, indispensable pour les investisseurs et décideurs.

### 1.2 Inflation et Prix
- **Objectif métier :** Suivre le pouvoir d'achat, le coût de la vie et le climat des affaires.
- **Type de données attendu :** Indices de prix (IPC - Indice des Prix à la Consommation global et ventilé par catégories).
- **Niveau géographique pertinent :** National, Régional (Départements, Aires métropolitaines vs Reste du pays).
- **Fréquence :** Mensuelle.
- **Difficultés potentielles :** Ruptures de séries lors des changements de l'année de base par l'IHSI ; collecte physique des prix parfois entravée par l'insécurité.
- **Valeur ajoutée pour le produit :** Permet une analyse fine de l'impact conjoncturel (crises, pénuries de carburant) sur le coût de la vie.

### 1.3 Démographie
- **Objectif métier :** Comprendre la taille du marché, la structure de la population et les dynamiques migratoires.
- **Type de données attendu :** Population totale, Pyramide des âges, Taux de natalité/mortalité, Flux migratoires (remises migratoires).
- **Niveau géographique pertinent :** National, Départemental, Communal.
- **Fréquence :** Annuelle (Estimations), Décennale (Recensement effectif).
- **Difficultés potentielles :** Absence de recensement récent et fiable (le dernier complet date d'il y a longtemps) ; fortes incertitudes sur les taux d'émigration réels.
- **Valeur ajoutée pour le produit :** Crucial pour les ONG et les entreprises (taille de marché), donne un dénominateur pour le calcul des indicateurs per capita.

### 1.4 Pauvreté
- **Objectif métier :** Mesurer la vulnérabilité économique, cibler les interventions de développement.
- **Type de données attendu :** Taux de pauvreté extrême (<2.15$/jour), Coefficient de Gini, IPC (Indice de Pauvreté Multidimensionnelle).
- **Niveau géographique pertinent :** National, Départemental (clivage urbain/rural).
- **Fréquence :** Annuelle à Pluriannuelle (enquêtes type ECVMAS).
- **Difficultés potentielles :** Données souvent issues de sondages internationaux ou de projections modélisées (Banque Mondiale) ; rareté des enquêtes ménages exhaustives récentes.
- **Valeur ajoutée pour le produit :** Indicateur phare pour les bailleurs de fonds (USAID, BM, BID) mesurant l'impact de leurs programmes.

### 1.5 Éducation
- **Objectif métier :** Évaluer le capital humain, l'accès à l'école et la qualité de la future force de travail.
- **Type de données attendu :** Taux d'alphabétisation, Taux de scolarisation brut/net (primaire, secondaire), Dépenses publiques en éducation.
- **Niveau géographique pertinent :** National, Départemental.
- **Fréquence :** Annuelle.
- **Difficultés potentielles :** Forte prédominance du secteur privé non régulé rendant la collecte de données sur les effectifs scolaires incomplète ou biaisée.
- **Valeur ajoutée pour le produit :** Utile pour évaluer le potentiel de développement à long terme et les besoins en formation.

### 1.6 Santé
- **Objectif métier :** Analyser le système de soins, l'espérance de vie et l'impact des crises sanitaires.
- **Type de données attendu :** Espérance de vie, Taux de mortalité infantile/maternelle, Taux de vaccination, Couverture sanitaire, Dépenses de santé.
- **Niveau géographique pertinent :** National, Départemental.
- **Fréquence :** Annuelle à Pluriannuelle (Enquête Mortalité, Morbidité et Utilisation des Services - EMMUS).
- **Difficultés potentielles :** Sous-déclaration dans les registres d'état civil ; système d'information sanitaire (SIS) fragmenté.
- **Valeur ajoutée pour le produit :** Analyse du développement humain pour les ONG médicales et organisations internationales.

### 1.7 Sécurité Alimentaire
- **Objectif métier :** Anticiper et gérer les crises humanitaires, comprendre l'inflation alimentaire.
- **Type de données attendu :** Classification de phases (cadre intégré IPC), Prix des denrées de base (riz, maïs, haricots), Taux de malnutrition.
- **Niveau géographique pertinent :** National, Départements et Communes très spécifiques.
- **Fréquence :** Mensuelle (prix) à Trimestrielle/Semestrielle (rapports CNSA).
- **Difficultés potentielles :** Volatilité extrême selon la saison cyclonique, la situation sécuritaire (routes bloquées) ; sources multiples à agréger (CNSA, PAM, FEWS NET).
- **Valeur ajoutée pour le produit :** Cas d'usage d'alerte précoce à très forte valeur humaine et politique.

### 1.8 Géographie et Territoire
- **Objectif métier :** Comprendre l'occupation des sols, l'accès aux ressources, et les vulnérabilités climatiques.
- **Type de données attendu :** Occupation des sols, Déforestation, Risques sismiques/climatiques, Données GIS (fichiers Shapefile de limites administratives).
- **Niveau géographique pertinent :** Coordonnées géographiques, raster, communal.
- **Fréquence :** Lente/Statique, excepté pour les événements climatiques.
- **Difficultés potentielles :** Nécessité de gérer des bases de données spatiales (PostGIS), volumétrie élevée pour du MVP.
- **Valeur ajoutée pour le produit :** Base pour une future version cartographique interactive (V2/V3), utile pour l'analyse des risques.

### 1.9 Infrastructures
- **Objectif métier :** Évaluer l'environnement logistique, énergétique et de communication.
- **Type de données attendu :** Accès à l'électricité, États des routes, Pénétration de l'internet / téléphonie mobile, Connexions portuaires/aéroportuaires.
- **Niveau géographique pertinent :** National, Régional (corridors économiques).
- **Fréquence :** Annuelle.
- **Difficultés potentielles :** Données très dispersées (MTPTC, EDH, CONATEL) et souvent déclaratives ou peu fiables.
- **Valeur ajoutée pour le produit :** Indicateur direct de la faisabilité commerciale ou logistique d'un investissement privé.

### 1.10 Gouvernance
- **Objectif métier :** Estimer la stabilité politique, l'efficacité institutionnelle et l'environnement légal.
- **Type de données attendu :** Indicateurs composite (ex: WGI de la Banque Mondiale - État de droit, corruption, stabilité politique), Nombre d'actes législatifs, Budget exécuté vs prévu.
- **Niveau géographique pertinent :** National.
- **Fréquence :** Annuelle ou Bi-annuelle.
- **Difficultés potentielles :** Les données quantitatives sont rares et souvent subjectives (perception de la corruption).
- **Valeur ajoutée pour le produit :** Complète le score de "Risque Pays" pour les investisseurs étrangers (Compliance, ESG).

---

## 2. Données Non Structurées (RAG / NLP)

### 2.1 Documents et Rapports Qualitatifs
- **Objectif métier :** Apporter le contexte, l'analyse experte et les prévisions narratives derrière les chiffres ("Le Pourquoi").
- **Type de données attendu :** Rapports Textuels en format PDF, Word, HTML.
  - *Monétaire / Financier :* Notes de la BRH, Rapports annuels de banques commerciales.
  - *Macroéconomique :* Rapports Art. IV du FMI, Revues IHSI.
  - *Développement / Social :* Études sectorielles de la Banque Mondiale, BID, USAID, PAM, CNSA.
  - *Légal :* Le Moniteur (Journal Officiel), Textes de loi, Décrets.
- **Niveau géographique pertinent :** Principalement National et macro-régional.
- **Fréquence :** Continue (dès publication intrajournalière à rapports annuels).
- **Difficultés potentielles :** 
  - Qualité des PDF (parfois des images scannées sans OCR).
  - Structure complexe (tableaux imbriqués, graphiques, notes de bas de page) difficile à ingérer par les parsers standards.
  - Multiplicité des abréviations institutionnelles à faire comprendre au LLM.
- **Valeur ajoutée pour le produit :** Constitue le cœur du moteur d'intelligence conversationnelle. C'est ici que l'Agent RAG excelle en résumant et en cherchant l'information enfouie dans des centaines de pages. Ce bloc crée le plus gros "Gain de Temps" pour le client.
