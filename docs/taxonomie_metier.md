# Taxonomie Métier : Haiti Data Intelligence

Ce document présente le dictionnaire métier structuré sous forme de taxonomie. Il constitue l'ontologie centrale du projet, servant de base pour l'indexation intelligente des documents (RAG), le routage NLP des questions utilisateurs, et le filtrage analytique dans le Dashboard.

---

## 1. Tableau Structuré (Taxonomie Centrale)

| Grand Domaine | Sous-Domaine | Indicateurs Associés | Concepts Connexes | Mots-clés & Synonymes (FR/EN/HT) |
| :--- | :--- | :--- | :--- | :--- |
| **MACRO-ÉCONOMIE** | **Production & Croissance** | PIB (Global, per capita), Taux de croissance, VAB sectorielle. | Récession, Secteur formel/informel, Chocs économiques. | GDP, PIB, Gross Domestic Product, Récession économique, Croissance, Valeur Ajoutée. |
| | **Monétaire & Change** | Taux de change HTG/USD, Taux directeur BRH, Réserves de change, Masse monétaire. | Dépréciation, Politique monétaire, Liquidité, Bons BRH. | Gourde, HTG, Dollars, USD, Taux de référence, Foreign exchange reserves, Politique de la BRH, Cash, Lajan. |
| | **Prix & Inflation** | IPC général, IPC alimentaire, Taux d'inflation (Glissement annuel). | Pouvoir d'achat, Coût de la vie, Chocs d'offre, Stagflation. | Inflation, Consumer Price Index, CPI, Hausse des prix, Panier de la ménagère, Lavi chè. |
| | **Finances Publiques** | Recettes fiscales, Dépenses publiques, Déficit budgétaire, Dette publique. | Fiscalité, Financement monétaire, DGI, AGD, Subventions. | Budget de l'État, Fiscal policy, Taxes, Dette externe/interne, Souveraineté financière, Douanes. |
| **COMMERCE & ÉCHANGES** | **Commerce Extérieur** | Balance commerciale, Importations, Exportations. | Déficit commercial, Partenaires commerciaux, Tarifs douaniers, Secteur textile. | Imports, Exports, Trade balance, Code douanier, Zone Franche, Parc Industriel (PIC). |
| | **Transferts & Diasporas** | Remises migratoires (Remittances), Investissements directs étrangers (IDE/FDI). | Migration, Fuite des cerveaux, Transferts sans contrepartie. | Transferts d'argent, Diaspora haïtienne, Western Union, CAM, FDI, Foreign Direct Investment. |
| **SOCIÉTÉ & DÉVELOPPEMENT**| **Travail & Emploi** | Taux de chômage, Taux d'activité, Emploi informel, Salaire minimum. | Précarité, CSS (Conseil Supérieur des Salaires), Code du travail. | Chômage, Unemployment, Job market, Sous-emploi, Travail au noir. |
| | **Pauvreté & Inégalités** | Taux de pauvreté, Indice de Gini, Indice de Développement Humain (IDH/HDI). | Vulnérabilité, Exclusion, Filets sociaux, Stratification. | Poverty, Gini coefficient, Human Development Index, Inégalité des revenus, Classe moyenne. |
| | **Sécurité Alimentaire** | Classification IPC (Phases 1-5), Prix du panier alimentaire, Prévalence de la malnutrition. | Faim, Urgence humanitaire, Campagne agricole, Importations alimentaires. | Food security, Insecurity, Famine, Malnutrition, PAM, CNSA, FEWS NET, Grangou. |
| **INFRASTRUCTURE & GOUVERNANCE**| **Gouvernance & Climat des Affaires**| Indice de perception de la corruption, Risque pays. | Instabilité politique, Insécurité, État de droit, Climat d'investissement. | Corruption, Political risk, Doing Business, Gangs, Sécurité, Kidnapping, Gouvernance publique. |
| | **Énergie & Logistique** | Accès à l'électricité, Prix du carburant, Connectivité. | Énergies renouvelables, Infrastructures routières, Port/Aéroport. | EDH, Diesel, Gazoline, Blackout, Routes nationales, APN. |

---

## 2. Dictionnaire Métier Synthétique (Mapping pour l'IA)

Ce dictionnaire map les concepts complexes pour le traitement du langage naturel (NLP).

*   **BRH (Banque de la République d'Haïti) :** La banque centrale. *Synonymes RAG :* Banque Centrale, Autorité monétaire, Central Bank of Haiti.
*   **IHSI (Institut Haïtien de Statistique et d'Informatique) :** Agence statistique nationale. *Synonymes RAG :* Institut de statistique, Bureau des statistiques, Haitian Institute of Statistics.
*   **Glissement Annuel :** Méthode de calcul de l'inflation (ex: Décembre 2023 par rapport à Décembre 2022). *Opposé à :* Variation mensuelle. *Attention RAG :* S'assurer que le LLM distingue "inflation annuelle" de "inflation en glissement mensuel".
*   **Financement Monétaire :** Le fait pour la BRH d'imprimer de la monnaie (créer de la liquidité) pour combler le déficit de l'État. *Concepts liés :* Monétisation du déficit, Création monétaire, Inflation.
*   **Remittances :** Fonds transférés par les Haïtiens vivant à l'étranger vers Haïti. *Synonymes :* Transferts privés, Envois de fonds, Diaspora funds. (Représente ~20% du PIB).

---

## 3. Relations entre Thèmes (Ontologie)

Pour permettre à l'IA de faire des déductions sémantiques ou des analyses croisées, les relations suivantes (Graphes Conceptuels) doivent être encodées dans les prompts ou les métadonnées :

*   `[Financement Monétaire]` **CAUSES** `[Dépréciation de la Gourde]` -> **CAUSES** `[Inflation Importée]`
*   `[Insécurité / Climat Politique]` **IMPACTS** `[Prix Locaux]` ET `[IDE / Investissements Directs Étrangers]`
*   `[Chocs Climatiques (Cyclones)]` **IMPACTS** `[Production Agricole]` -> **IMPACTS** `[Sécurité Alimentaire]` ET `[Importations Alimentaires]`
*   `[Remises Migratoires]` **SOUTIENT** `[Consommation des Ménages]` ET `[Réserves de Change de la BRH]`

---

## 4. Recommandations d'Utilisation dans le Produit

### A. Ingestion Documentaire (Chunking & Embedding)
- Appliquer un taggage sémantique (metadata) lors de la vectorisation (ex: associer la méta-donnée `category: 'macroeconomics', subcategory: 'inflation'` à un chunk).
- Améliorer les embeddings textuels en ajoutant discrètement aux chunks de texte des "Keywords enrichis" issus de la taxonomie, pour aider à la recherche (par exemple, si le document parle de "lavi chè", injecter "inflation, CPI" dans le chunk caché).

### B. Routage des Questions (LLM Router)
- Utiliser la taxonomie pour classer l'intention de l'utilisateur ("Intent Detection"). Si la question contient "taux directeur", l'agent sachant que c'est de la "Monétaire & Change" cherchera prioritairement dans l'index spécifique des "Notes sur la Politique Monétaire".
- Créer un système hybride : si la requête relève du "Macro-Économie/Données Structurées" (ex: "Quel est le PIB de 2020 ?"), router la question vers la Base de Données SQL (Graphique) plutôt que vers les documents (RAG).

### C. Interface Utilisateur (Dashboard & Filtres)
- Utiliser la hiérarchie `[Grand Domaine] > [Sous-Domaine] > [Indicateur]` pour structurer les menus déroulants du Dashboard interactif, afin de rendre la navigation intuitive pour un économiste.

### D. Génération de Réponses (Prompt Engineering)
- Fournir un extrait de ce dictionnaire dans le "*System Prompt*" de l'LLM, particulièrement pour lui expliquer les relations de cause à effet propres à Haïti (ex: "Note: En Haïti, la dépréciation du taux de change a un impact immédiat sur l'inflation car l'économie est fortement importatrice."). Cela réduira les hallucinations et améliorera la qualité du raisonnement des briefings.
