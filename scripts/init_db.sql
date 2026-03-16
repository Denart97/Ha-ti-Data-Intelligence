-- =============================================================================
-- PROJET : Haiti Data Intelligence (HDI)
-- SCRIPT : Initialisation du schéma de base de données (PostgreSQL)
-- AUTEUR : Antigravity AI
-- DATE   : 2026-03-16
-- =============================================================================

/*
   EXPLICATION D'EXÉCUTION :
   1. Ce script doit être exécuté par un utilisateur disposant des droits de création de tables.
   2. Il est recommandé de créer une base de données dédiée : CREATE DATABASE haiti_data_intelligence;
   3. Exécution via psql : psql -d haiti_data_intelligence -f init_db.sql

   REMARQUES SUR LES PERFORMANCES :
   - Utilisation de UUID pour les PK : Garantit l'unicité globale et facilite les migrations/synchronisations.
   - Index Composés : Optimisés pour les accès fréquents du Dashboard (Séries temporelles).
   - Partitionnement (Optionnel futur) : La table 'valeurs_indicateurs' pourra être partitionnée par pays ou indicateur si le volume dépasse 10M de lignes.

   HYPOTHÈSES :
   - Les codes ISO Alpha-3 sont la référence unique pour les pays.
   - Les indicateurs utilisent une taxonomie métier interne (ex: GDP_REAL) pour découpler des codes sources (ex: NY.GDP.MKTP.KD.ZG).
   - Le versionnage est géré par la date d'ingestion et le statut (PROVISOIRE vs FINAL).
*/

-- Activer l'extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. CORE DATA (DONNÉES STRUCTURELLES)
-- -----------------------------------------------------------------------------

-- Table : pays
CREATE TABLE IF NOT EXISTS pays (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    iso_alpha3 VARCHAR(3) UNIQUE NOT NULL,
    nom_fr VARCHAR(100) NOT NULL,
    nom_en VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_pays_iso ON pays (iso_alpha3);

-- Table : sources
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom VARCHAR(100) UNIQUE NOT NULL,
    type_institution VARCHAR(50), -- Nationale, Internationale, ONG
    fiabilite_score INT CHECK (fiabilite_score >= 0 AND fiabilite_score <= 10),
    site_web VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table : datasets
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    code_dataset VARCHAR(100) NOT NULL, -- ex: 'WDI', 'API_BRH'
    url_origine TEXT,
    frequence_maj VARCHAR(20), -- ANNUEL, MENSUEL, QUOTIDIEN
    last_updated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table : indicateurs
CREATE TABLE IF NOT EXISTS indicateurs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_indicateur VARCHAR(50) UNIQUE NOT NULL, -- ex: 'INFLATION_GA'
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    unite_mesure VARCHAR(50),
    grand_domaine VARCHAR(100), -- MACRO, MONETAIRE, SOCIAL, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_indicateurs_domaine ON indicateurs (grand_domaine);

-- Table : valeurs_indicateurs (Table des faits)
CREATE TABLE IF NOT EXISTS valeurs_indicateurs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicateur_id UUID REFERENCES indicateurs(id) ON DELETE CASCADE,
    pays_id UUID REFERENCES pays(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id),
    date_valeur DATE NOT NULL,
    valeur_numerique NUMERIC(20, 6),
    statut VARCHAR(20) DEFAULT 'FINAL', -- PROVISOIRE, FINAL, REVISE
    date_ingestion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB, -- Pour stocker des attributs additionnels sans changer le schéma
    
    UNIQUE (indicateur_id, pays_id, date_valeur, statut)
);
-- Index crucial pour les graphiques temporels et comparaisons
CREATE INDEX idx_valeurs_lookup ON valeurs_indicateurs (indicateur_id, pays_id, date_valeur DESC);

-- -----------------------------------------------------------------------------
-- 2. MODÈLE DOCUMENTAIRE (RAG)
-- -----------------------------------------------------------------------------

-- Table : documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id),
    titre VARCHAR(255) NOT NULL,
    date_publication DATE,
    url_pdf TEXT,
    content_hash VARCHAR(64) UNIQUE, -- SHA-256
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table : chunks_documentaires
CREATE TABLE IF NOT EXISTS chunks_documentaires (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    vector_id VARCHAR(100) UNIQUE, -- Lien vers ChromaDB
    page_numero INT,
    texte_contenu TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. AUDIT & TRAÇABILITÉ AI (LLMOps)
-- -----------------------------------------------------------------------------

-- Table : requetes_utilisateur
CREATE TABLE IF NOT EXISTS requetes_utilisateur (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    texte_brut TEXT NOT NULL,
    type_routage VARCHAR(20), -- SQL, RAG, HYBRID, ERROR
    identifiant_session VARCHAR(100),
    tokens_consommes INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table : briefings_generes
CREATE TABLE IF NOT EXISTS briefings_generes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requete_id UUID REFERENCES requetes_utilisateur(id),
    contenu_markdown TEXT NOT NULL,
    score_feedback_utilisateur INT DEFAULT 0, -- -1, 0, 1
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table : citations
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    briefing_id UUID REFERENCES briefings_generes(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks_documentaires(id),
    numero_reference INT NOT NULL, -- L'index [n] dans le texte
    metadata JSONB
);

-- Table : comparisons (Historique des vues comparatives)
CREATE TABLE IF NOT EXISTS comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requete_id UUID REFERENCES requetes_utilisateur(id),
    indicateur_id UUID REFERENCES indicateurs(id),
    pays_base_id UUID REFERENCES pays(id),
    pays_cible_id UUID REFERENCES pays(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- VUES UTILES
-- -----------------------------------------------------------------------------

-- Vue pour obtenir la dernière valeur "Finale" de chaque indicateur par pays
CREATE OR REPLACE VIEW vue_derniers_indicateurs AS
SELECT DISTINCT ON (indicateur_id, pays_id)
    p.iso_alpha3,
    i.code_indicateur,
    v.date_valeur,
    v.valeur_numerique,
    v.statut
FROM valeurs_indicateurs v
JOIN pays p ON v.pays_id = p.id
JOIN indicateurs i ON v.indicateur_id = i.id
WHERE v.statut = 'FINAL'
ORDER BY indicateur_id, pays_id, v.date_valeur DESC;
