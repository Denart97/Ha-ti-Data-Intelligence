# Schéma de Base de Données : Haiti Data Intelligence

Ce document définit le modèle relationnel (PostgreSQL) de la plateforme. 
Il combine le monde de la Data Structurée (Séries macroéconomiques), la gestion des métadonnées du monde Vectoriel (RAG), et la traçabilité des opérations de l'IA (LLMOps).

La nomenclature suit un formalisme Snake Case standard. Type de clés primaires : `UUID` (universally unique identifier) privilégié pour la sécurité et la distribution.

---

## 1. Modèle de Données (Core Data)

### 1.1 Table : `pays`
- **Rôle :** Gérer les pays pour les comparaisons macroéconomiques.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `iso_alpha3` (VARCHAR(3), *ex: 'HTI', 'DOM'*)
  - `nom_fr` (VARCHAR)
  - `nom_en` (VARCHAR)
- **Index :** `iso_alpha3` (UNIQUE).
- **Justification :** Permet la normalisation des requêtes comparatives inter-pays (évite les fautes de frappe sur 'Haïti' vs 'Haiti').

### 1.2 Table : `sources`
- **Rôle :** Identifier l'institution émettrice pour justifier l'autorité de la donnée.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `nom` (VARCHAR, *ex: 'Banque Mondiale', 'BRH'*)
  - `type_institution` (VARCHAR, *ex: 'Nationale', 'Internationale'*)
  - `fiabilite_score` (INT, sur 10)
- **Index :** `nom` (UNIQUE).

### 1.3 Table : `datasets`
- **Rôle :** Représenter un fichier ou un endpoint API d'une source donnée (ex: API WB `NY.GDP.MKTP.CD`).
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `source_id` (UUID, FK -> sources.id)
  - `code_dataset` (VARCHAR)
  - `url_origine` (VARCHAR)
  - `frequence_maj` (VARCHAR, *ex: 'ANNUEL', 'MENSUEL'*)
  - `last_updated_at` (TIMESTAMP)

### 1.4 Table : `indicateurs`
- **Rôle :** Définir la variable économique.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `code_indicateur` (VARCHAR, UNIQUE, *ex: 'PIB_CROISSANCE', 'INFLATION_GA'*)
  - `nom` (VARCHAR)
  - `description` (TEXT)
  - `unite_mesure` (VARCHAR, *ex: '%', 'Milliards USD', 'HTG'*)
  - `grand_domaine` (VARCHAR, *issu de la taxonomie métier*)
- **Index :** `code_indicateur` (UNIQUE), `grand_domaine`.

### 1.5 Table : `valeurs_indicateurs` (La table des faits)
- **Rôle :** Stocker toutes les valeurs des séries temporelles.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `indicateur_id` (UUID, FK -> indicateurs.id)
  - `pays_id` (UUID, FK -> pays.id)
  - `dataset_id` (UUID, FK -> datasets.id)
  - `date_valeur` (DATE, *si annuel, mis au 31/12*)
  - `valeur_numerique` (NUMERIC)
  - `statut` (VARCHAR, *ex: 'PROVISOIRE', 'FINAL'*)
- **Index :** Index composé sur `(indicateur_id, pays_id, date_valeur)` pour accélérer l'affichage des graphiques temporels.

---

## 2. Modèle Documentaire (Pont avec ChromaDB)

Bien que ChromaDB contienne les vecteurs, conserver les métadonnées dans PostgreSQL permet des jointures et un audit robuste.

### 2.1 Table : `documents`
- **Rôle :** Référencer le rapport PDF original source du RAG.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `source_id` (UUID, FK -> sources.id)
  - `titre` (VARCHAR)
  - `date_publication` (DATE)
  - `url_pdf` (VARCHAR)
  - `content_hash` (VARCHAR, *SHA-256 du fichier pour éviter les doublons*)

### 2.2 Table : `chunks_documentaires`
- **Rôle :** Stocker le texte du paragraphe découpé pour pouvoir afficher la citation exacte sans interroger la DB Vectorielle inutilement.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `document_id` (UUID, FK -> documents.id)
  - `vector_id` (VARCHAR, *l'ID exact dans ChromaDB*)
  - `page_numero` (INT)
  - `texte_contenu` (TEXT)
- **Index :** `vector_id` (UNIQUE).

---

## 3. Modèle d'Audit et de Traçabilité AI (LLMOps)

### 3.1 Table : `requetes_utilisateur`
- **Rôle :** Tracer les intentions des utilisateurs.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `texte_brut` (TEXT, *ex: 'Quel est le PIB d'Haïti ?'*)
  - `type_routage` (VARCHAR, *'SQL', 'RAG', 'HYBRID', 'ERROR'*)
  - `tokens_consommes` (INT, *coût LLM*)
  - `created_at` (TIMESTAMP)

### 3.2 Table : `comparisons`
- **Rôle :** Sauvegarder l'état des dashboards comparatifs pour le futur (Historique).
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `requete_id` (UUID, FK -> requetes_utilisateur.id)
  - `indicateur_id` (UUID, FK -> indicateurs.id)
  - `pays_base_id` (UUID, FK -> pays.id)
  - `pays_cible_id` (UUID, FK -> pays.id)

### 3.3 Table : `briefings_generes`
- **Rôle :** Stocker la synthèse narrative du LLM.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `requete_id` (UUID, FK -> requetes_utilisateur.id)
  - `contenu_markdown` (TEXT)
  - `score_feedback_utilisateur` (INT, *+1 ou -1 pour le RLHF*)
  - `created_at` (TIMESTAMP)

### 3.4 Table : `citations`
- **Rôle :** La jointure de vérité. Associe un briefing généré aux documents exacts qui l'ont justifié.
- **Colonnes & Types :**
  - `id` (UUID, PK)
  - `briefing_id` (UUID, FK -> briefings_generes.id)
  - `chunk_id` (UUID, FK -> chunks_documentaires.id)
  - `numero_reference` (INT, *L'index de citation [1], [2] dans le texte*)

---

## 4. Stratégie de Gouvernance des Données DB

1.  **Mécanisme de Fraîcheur :**
    *   La table `datasets` contient `last_updated_at`. Le système de cron ETL lit cette date et ne télécharge via API que les données postérieures (Delta Load).
2.  **Harmonisation des Unités :**
    *   Le module `data_engine` devra TOUJOURS convertir les valeurs locales dans l'unité spécifiée par la table `indicateurs` lors du pipeline ETL. Exemple : Si l'investisseur demande le PIB en USD, et que la BRH le donne en Milliards de Gourdes, l'ETL stocke la valeur calculée dans la table `valeurs_indicateurs` et non la valeur brute, pour garantir la fluidité du Dashboard.
3.  **Gestion du Versionnage (Append-Only) :**
    *   Si l'IHSI révise les valeurs d'inflation de 2022 (fréquent). On n'efface pas les données (pas de DELETE). 
    *   On insère la nouvelle ligne dans `valeurs_indicateurs` avec la même date, mais on la marque comme `statut='FINAL'`. La vue SQL interrogée par le Dashboard est filtrée pour ne prendre que la ligne la plus récente pour une date donnée (via un `WINDOW FUNCTION` type `ROW_NUMBER() OVER (PARTITION BY date_valeur ORDER BY created_at DESC)`).
4.  **Métadonnées étendues :**
    *   Ajout (potentiel en V2) d'une colonne de type `JSONB` sur `documents` et `valeurs_indicateurs` pour stocker des attributs d'extraction bruts sans casser le schéma relationnel.
