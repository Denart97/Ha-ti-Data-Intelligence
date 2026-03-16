# Stratégie de Normalisation et d'Harmonisation : Haiti Data Intelligence

Ce document définit les règles de transformation à appliquer aux données brutes extraites (étape T de l'ETL) avant leur insertion dans la base de données relationnelle cible. Il s'assure de l'intégrité, de la comparabilité et de la propreté des séries temporelles.

---

## 1. Schéma de Transformation Logique

```text
[ Data Brute (Hétérogène) ]
         │
         ▼
[ 1. Alignement Période & Fréquence ] ----> (Dates fixées au YYYY-MM-DD, Années fiscales traitées)
         │
         ▼
[ 2. Résolution Géographique      ] ----> (Mapping 'Haiti', 'HT' -> 'HTI')
         │
         ▼
[ 3. Harmonisation des Unités     ] ----> (Conversion Millions -> Milliards, % formatés)
         │
         ▼
[ 4. Standardisation des Thèmes   ] ----> (Mapping vers la taxonomie interne)
         │
         ▼
[ 5. Traitement Valeurs Manquantes] ----> (NaN -> Null, ou Interpolation selon la règle)
         │
         ▼
[ 6. Résolution des Conflits      ] ----> (Arbitrage Source A vs Source B)
         │
         ▼
[ Data Nette & Prête à l'Emploi (Table: valeurs_indicateurs) ]
```

---

## 2. Règles d'Harmonisation par Domaine

### 2.1 Harmonisation des noms de pays
- **Le Problème :** En français, on peut trouver "Haïti", "Haiti", "République d'Haïti". En anglais "Haiti", "Republic of Haiti".
- **La Règle :** Le nom "display" (d'affichage) est stocké une seule fois dans la table `pays`. Lors de l'ETL, on ne map jamais sur le nom textuel brut, on utilise toujours une table de correspondance (Dictionnaire interne) pour convertir la chaîne textuelle brute vers l'UUID interne du pays.

### 2.2 Harmonisation des codes pays
- **La Règle :** Utilisation stricte de la norme internationale **ISO 3166-1 alpha-3**.
- **Exemples :** Haïti = `HTI`, République Dominicaine = `DOM`, États-Unis = `USA`. Ce code sert d'identifiant naturel garant et unique lors du traitement des DataFrames Pandas avant l'insertion en base de données.

### 2.3 Harmonisation des dates
- **Le Problème :** 
  - L'année fiscale haïtienne va d'octobre (N-1) à septembre (N).
  - Les données mensuelles arrivent parfois au format "Mars 2023" ou "2023M03".
- **La Règle (Format ISO 8601) :**
  - Le champ en base `date_valeur` est obligatoirement du type `DATE` (YYYY-MM-DD).
  - Pour une **donnée annuelle**, on fixe par convention le jour au 31 Décembre : `2023-12-31`.
  - Pour une **donnée mensuelle**, on fixe par convention le dernier jour du mois : `2023-03-31`.
  - *Gestion Année Fiscale :* Si la source (ex: BRH) indique expressément "Exercice fiscal 2023", la date est stockée au `2023-09-30`. Le Dashboard devra contenir une fonction "Vue Année Fiscale vs Civile".

### 2.4 Harmonisation des unités
- **Le Problème :** Le PIB peut être fourni en Gourdes courantes, Gourdes constantes 1986, ou USD.
- **La Règle de Master Data :** L'unité cible "de vérité" est définie en dur dans la table `indicateurs`. 
- **Conversions obligatoires :**
  - **Pourcentages :** Stockés en format décimal (`0.05` pour 5%) dans le Backend. Le x100 est réservé au Frontend.
  - **Devise :** Toute valeur en unité locale (Millions de Gourdes) vs (Milliards de Gourdes) est harmonisée à l'échelle supérieure si on manipule d'énormes agrégats (Milliards). Le taux de conversion HTG/USD de fin de période sera utilisé si besoin.

### 2.5 Harmonisation des fréquences
- **Le Problème :** Vouloir afficher un même graphique mixant des données mensuelles et annuelles.
- **La Règle :** Au niveau du stockage (`valeurs_indicateurs`), la fréquence native est respectée. C'est le **Moteur Analytique (API Backend)** qui gère l'agrégation "on-the-fly". Si l'utilisateur demande l'inflation annuelle, le backend prend la moyenne (ou la dernière valeur selon l'indicateur: *Average* vs *Last*) des 12 valeurs mensuelles et les retourne au Frontend.

### 2.6 Gestion des valeurs manquantes (Missing Values)
- **Le Problème :** Une source ne publie pas le chiffre d'un trimestre. On retrouve des "N/A", "--", "".
- **La Règle de Stockage :** En base de données SQL, toute valeur manquante est stricto sensu stockée en vrai `NULL`. Pas de zéros (0 n'est pas NULL) ni de valeurs fantômes (ex: -9999).
- **La Règle d'Affichage :**
  - Pour les séries temporelles strictes : L'API retourne Null, le graphique brise la ligne (Line Chart broken).
  - *Interpolation (Optionnel V2) :* Si demandé, l'API backend peut interpoler linéairement (`df.interpolate()`) mais doit retourner un flag `is_estimated = true` pour afficher le pont du graphique en tiretés (ligne pointillée). L'UI ne doit jamais induire en erreur avec une donnée inventée par l'interpolation sans l'indiquer.

### 2.7 Gestion des conflits entre sources
- **Le Problème :** La croissance du PIB est de -1.8% selon l'IHSI et de -2.2% selon la Banque Mondiale pour 2023.
- **La Règle (Multi-Versionning Control) :**
  - On stocke les DEUX valeurs dans la base `valeurs_indicateurs`, chacune rattachée à son `dataset_id` (et donc à sa source respective).
  - Le frontend résout le conflit via le menu déroulant : "Sélectionner la source" (Défaut : Banque Mondiale pour l'international, IHSI pour le zoom national).
  - Au moment d'encapsuler la donnée dans les outils RAG/Génération de texte : Le LLM-Router injectera TOUJOURS la phrase : *"Selon la source X, la valeur est Y."*

### 2.8 Standardisation des thèmes et indicateurs
- **Le Problème :** L'API World Bank nomme l'indicateur `"NY.GDP.MKTP.KD.ZG"`, la BRH le nomme `"Taux de Croiss. Economique"`.
- **La Règle (UUID Mapping) :** 
  - La taxonomie métier dicte la norme via la table `indicateurs` (`code_indicateur = PIB_CROISSANCE`).
  - Le pipeline ETL chargeant la Banque Mondiale inclut un dictionnaire de translation stricte : `{"NY.GDP.MKTP.KD.ZG": "PIB_CROISSANCE"}`.
  - Peu importe le nom de colonne d'origine dans le fichier source, en sortie de l'ETL, le "Topic" a été normalisé. Tout passe par cet identifiant métier robuste.
