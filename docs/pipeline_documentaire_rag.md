# Pipeline Documentaire RAG : Haiti Data Intelligence

Ce document définit la stratégie complète de traitement des documents non structurés pour alimenter le moteur de Retrieval-Augmented Generation (RAG).

---

## 1. Étapes du Pipeline

### 1.1 Collecte (Ingestion)
*   **Sources :** BRH (Monetary Notes), FMI (Art. IV Reports), Banque Mondiale (Policy Papers).
*   **Mécanisme :** Crawler asynchrone détectant les nouveaux PDFs via checksum (MD5/SHA-256) pour éviter les doublons binaires.

### 1.2 Parsing & Extraction de Texte
*   **Outils :** `PyMuPDF` (Fitz) pour le texte brut, `pdfplumber` pour la structure complexe.
*   **Approche :** Extraction ordonnée conservant la hiérarchie des titres (H1, H2) via l'analyse de la taille des polices (si possible).

### 1.3 Nettoyage & Suppression du Bruit
*   **Bruit à supprimer :** 
    - En-têtes et pieds de page répétitifs (reconnaissance de motifs récurrents par page).
    - Numéros de page isolés.
    - Mentions légales redondantes en bas de page.
    - Caractères spéciaux issus d'un mauvais encodage.
*   **Normalisation :** Conversion en UTF-8 NFC, suppression des espaces multiples.

### 1.4 Découpage en Chunks (Chunking)
*   **Stratégie :** `RecursiveCharacterTextSplitter`.
*   **Unité :** Découpage par paragraphes pour préserver l'unité de sens.

### 1.5 Enrichissement par Métadonnées
Chaque chunk est "décoré" avec un contexte global pour améliorer la pertinence lors de la recherche vectorielle (Vector Search).

### 1.6 Détection des Doublons & Versionnage
*   **Doublons sémantiques :** Comparaison des embeddings au niveau du document.
*   **Versionnage :** Si un rapport est révisé, on conserve l'ancien mais on marque le nouveau comme `is_latest: true`.

### 1.7 Indexation Vectorielle
*   **Modèle :** `text-embedding-3-small` ou `multilingual-e5-large`.
*   **Stockage :** ChromaDB avec persistence liée aux IDs PostgreSQL.

---

## 2. Recommandations Stratégiques

### 2.1 Configuration du Chunking
*   **Taille des chunks :** **512 à 1024 tokens**. C'est le compromis idéal pour capturer une idée économique complète sans perdre la précision.
*   **Overlap (Recouvrement) :** **10% à 15% (soit ~100 tokens)**. Crucial pour ne pas couper une phrase ou une définition à l'endroit précis où le LLM en aurait besoin.

### 2.2 Métadonnées Obligatoires (Payload)
Pour chaque chunk, le vecteur doit embarquer :
- `source` : Institution (ex: BRH).
- `date_publication` : YYYY-MM-DD (pour le filtrage chronologique).
- `titre_document` : Pour la citation.
- `page_number` : Pour renvoyer l'utilisateur au bon endroit.
- `domaine` : Macro, Sécurité, etc. (pour le filtrage thématique).

### 2.3 Gestion des Cas Particuliers
*   **Documents longs (ex: Rapport Annuel BRH) :** Utilisation d'un "Contextual Header". Chaque chunk commence par : *"Document: [Titre], Section: [Chapitre]..."* pour donner du contexte au vecteur.
*   **Rapports Techniques :** Extraction prioritaire des légendes de tableaux et de graphiques. Si un paragraphe commente un tableau, le lien doit être maintenu.
*   **Définitions d'indicateurs :** Création d'un index vectoriel séparé pour les "Concepts Métier" (Glossaire) afin que le LLM sache toujours définir un terme comme le "Financement Monétaire" avant de commenter les chiffres.

### 2.4 Qualité et Incohérences
*   **Garde-fou :** Si le texte extrait d'une page PDF contient plus de 20% de symboles non lisibles, le document est envoyé en file d'attente "OCR Manuel".
*   **Citation :** Toute réponse générée doit obligatoirement inclure un lien cliquable vers le PDF source original.
