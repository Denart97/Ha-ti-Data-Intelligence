# Schéma de Données Harmonisé : Haiti Data Intelligence

Ce document définit le modèle de données cible unique permettant de stocker et d'unifier les informations provenant de sources hétérogènes (Banque Mondiale, FMI, BRH, IHSI). Il est conçu pour supporter à la fois les analyses quantitatives (SQL) et qualitatives (RAG).

---

## 1. Référentiels Géo-Temporels

### 1.1 Table : `territoires`
- **Rôle :** Gérer la hiérarchie géographique d'Haïti et les pays comparateurs.
- **Colonnes :**
  - `id` (UUID, PK)
  - `parent_id` (UUID, FK -> territoires.id, *NULL pour Haïti ou pays étrangers*)
  - `type_niveau` (VARCHAR, *ex: 'PAYS', 'DEPARTEMENT', 'COMMUNE', 'SECTION'*)
  - `code_officiel` (VARCHAR, *ISO3 pour pays, Code IHSI pour Haïti*)
  - `nom_fr` (VARCHAR)
  - `geometry` (GEOMETRY, *Optionnel PostGIS*)
- **Justification :** Permet de stocker l'inflation nationale (IHSI) tout en descendant au niveau départemental si la source le permet.

### 1.2 Table : `sources`
- **Rôle :** Centraliser les fournisseurs de données.
- **Colonnes :**
  - `id` (UUID, PK)
  - `nom` (VARCHAR, UNIQUE)
  - `type_institution` (VARCHAR)
  - `base_url` (VARCHAR)
  - `default_confidence_score` (DECIMAL, *0.0 à 1.0*)

---

## 2. Métadonnées & Séries Temporelles

### 2.1 Table : `indicateurs`
- **Rôle :** Dictionnaire central des variables économiques.
- **Colonnes :**
  - `id` (UUID, PK)
  - `code_identifiant` (VARCHAR, UNIQUE, *ex: 'HTI_GDP_GROWTH'*)
  - `label_fr` (VARCHAR)
  - `description` (TEXT)
  - `unite` (VARCHAR, *ex: '%', 'USD', 'HTG'*)
  - `frequence_standard` (VARCHAR, *'A', 'Q', 'M'*)

### 2.2 Table : `valeurs_indicateurs`
- **Rôle :** Entrepôt unique des faits numériques.
- **Colonnes :**
  - `id` (UUID, PK)
  - `territoire_id` (UUID, FK -> territoires.id)
  - `indicateur_id` (UUID, FK -> indicateurs.id)
  - `source_id` (UUID, FK -> sources.id)
  - `date_valeur` (DATE)
  - `valeur` (NUMERIC)
  - `statut_qualite` (VARCHAR, *ex: 'PROVISOIRE', 'FINAL', 'ESTIME'*)
  - `score_confiance_donnee` (DECIMAL, *0.0 à 1.0*)
- **Index :** `(territoire_id, indicateur_id, date_valeur)`

---

## 3. Stockage Documentaire & RAG

### 3.1 Table : `documents`
- **Rôle :** Référentiel des documents textuels ingérés.
- **Colonnes :**
  - `id` (UUID, PK)
  - `source_id` (UUID, FK -> sources.id)
  - `titre` (VARCHAR)
  - `date_publication` (DATE)
  - `hash_contenu` (VARCHAR, UNIQUE)
  - `url_stockage` (VARCHAR)

### 3.2 Table : `chunks_documentaires`
- **Rôle :** Segments de texte pour la recherche vectorielle.
- **Colonnes :**
  - `id` (UUID, PK)
  - `document_id` (UUID, FK -> documents.id)
  - `vector_id` (VARCHAR, *Lien vers ChromaDB*)
  - `texte` (TEXT)
  - `page_num` (INT)

---

## 4. Traçabilité & Intelligence Artificielle

### 4.1 Table : `historique_collecte` (ETL Telemetry)
- **Rôle :** Journaliser chaque exécution de pipeline.
- **Colonnes :**
  - `id` (UUID, PK)
  - `source_id` (UUID, FK -> sources.id)
  - `timestamp_debut` (TIMESTAMP)
  - `status` (VARCHAR, *'SUCCESS', 'FAILED'*)
  - `records_count` (INT)
  - `logs_technique` (JSONB)

### 4.2 Table : `citations`
- **Rôle :** Justifier les réponses générées par le LLM.
- **Colonnes :**
  - `id` (UUID, PK)
  - `reponse_id` (UUID)
  - `chunk_id` (UUID, FK -> chunks_documentaires.id)
  - `pertinence_score` (DECIMAL)

---

## 5. Stratégie de Qualité et Confiance

*   **Gestion des Incohérences :** Si deux sources (`source_id`) fournissent une valeur pour le même `(territoire, indicateur, date)`, le système affiche en priorité celle ayant le `score_confiance_donnee` le plus élevé.
*   **Versionnage :** Toute mise à jour d'une valeur existante archive l'ancienne version dans une table `audit_valeurs` avant modification.
*   **Intégrité RAG :** Le `vector_id` assure la synchronisation stricte entre la base relationnelle et la base vectorielle.
