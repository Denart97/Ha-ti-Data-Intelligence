# Stratégie d'Embeddings et d'Indexation Vectorielle : Haiti Data Intelligence

Ce document définit les choix techniques et l'organisation de la base de données vectorielle pour garantir des performances optimales du moteur RAG, tout en restant dans le cadre d'un MVP réaliste.

---

## 1. Choix du Modèle d'Embeddings

Pour un projet traitant des données d'Haïti (Français majoritaire, Anglais institutionnel, Créole Haïtien local), le choix du modèle est critique.

*   **Modèle recommandé :** `multilingual-e5-large` (ou `text-embedding-3-small` via API OpenAI pour la simplicité du MVP).
*   **Justification :** 
    - **Multilinguisme :** Capacité native à aligner sémantiquement des questions en Français avec des documents en Anglais (et vice-versa).
    - **Performance :** Excellent rapport entre dimension du vecteur (1024 pour E5) et précision du "Retrieval".
    - **Coût :** Modèle open-source (hébergeable localement ou sur HF) ou API OpenAI peu onéreuse.

## 2. Stratégie d'Indexation

L'indexation n'est pas une simple injection de texte ; elle est structurée pour faciliter la recherche sémantique.

1.  **Pré-traitement :** Chaque chunk est nettoyé (retrait des headers/footers) avant vectorisation.
2.  **Préfixage sémantique :** (Si utilisation d'E5) Ajout du préfixe `query: ` pour les questions et `passage: ` pour les documents indexés afin d'optimiser la mesure de similarité cosinus.
3.  **Hachage :** Avant d'indexer un document, on vérifie si son `hash_contenu` existe déjà dans PostgreSQL pour éviter la ré-indexation inutile.

## 3. Organisation des Collections (ChromaDB)

Nous ne mettons pas tout dans un seul gros sac. Nous séparons les collections pour permettre des recherches ciblées (Routage).

| Nom de Collection | Contenu | Usage |
| :--- | :--- | :--- |
| `economic_reports` | Rapports BRH, FMI, BM (Le corps du texte). | Recherche documentaire générale. |
| `policy_notes` | Décisions, circulaires, arrêtés (Le Moniteur). | Recherche sur la gouvernance et les lois. |
| `indicator_definitions` | Glossaire et méthodologies des indicateurs. | Aide le LLM à définir les termes techniques. |
| `media_news` (V2/V3) | Articles de presse et fils RSS. | Veille conjoncturelle. |

## 4. Métadonnées de Filtrage (Pre-filtering)

L'indexation vectorielle est complétée par des métadonnées stockées dans ChromaDB pour permettre un "Hard Filtering" (ex: "Cherche uniquement dans les rapports de 2023").

*   `source`: (ex: 'BRH', 'IMF')
*   `date_iso`: (ex: '2023-10-01')
*   `geo_level`: (ex: 'NATIONAL', 'SUD')
*   `topic`: (ex: 'INFLATION', 'PIB')
*   `document_id`: Lien vers la table PostgreSQL `documents`.

## 5. Gestion du Multilingue (Translation Alignment)

Le système doit être "Cross-Lingual" :
*   **Question en Kreyòl :** Le modèle d'embedding multilingue doit être capable de trouver des chunks en Français/Anglais pertinents.
*   **Vérification :** Lors de l'indexation, on peut ajouter une métadonnée `language` pour permettre au LLM de savoir s'il doit traduire ou synthétiser la réponse.

## 6. Mécanisme de Mise à Jour et Réindexation

*   **Incrémentalité :** L'indexation est itérative. Seuls les nouveaux documents (hash inconnu) passent dans le pipeline d'embeddings.
*   **Réindexation Totale (Full Reindex) :** Exceptionnelle (si changement de modèle d'embeddings). Le pipeline doit être automatisable via un script `rebuild_vector_index.py`.
*   **Suppression :** Si un document est supprimé dans PostgreSQL, son `document_id` est utilisé pour appeler `collection.delete(where={"document_id": "..."})` dans ChromaDB.

## 7. Optimisation Performance / Coût

1.  **Dimensionalité :** Pour le MVP, utiliser des vecteurs de taille raisonnable (768 ou 1024). Inutile de monter à 3072 tokens si le volume documentaire est < 10,000 documents.
2.  **Top-K Retrieval :** Retourner les **5 à 10 chunks** les plus pertinents. Trop de chunks augmentent le coût du token d'entrée du LLM et le risque de confusion ("Lost in the Middle").
3.  **Persistance Locale :** Utiliser ChromaDB en mode local (duckdb/parquet) pour éviter les frais d'hébergement d'une base managée (Pinecone/Milvus) au démarrage.

## 8. Résumé Technique pour le MVP

*   **Embedding Engine :** OpenAI `text-embedding-3-small` (Efficace, pas de serveur à gérer).
*   **Vector Store :** ChromaDB (Local persistence).
*   **Chunking :** 800 tokens, overlap 100.
*   **Filtrage :** Basé sur la date et l'institution.
