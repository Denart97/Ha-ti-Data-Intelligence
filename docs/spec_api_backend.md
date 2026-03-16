# Spécification de l'API Backend : Haiti Data Intelligence

Ce document définit les contrats d'interface (API REST) du backend. L'API est construite avec **FastAPI** et suit les principes REST.

---

## 1. Endpoints de Base et Monitoring

### `GET /health`
*   **Rôle :** Vérifier la disponibilité des services (API, DB, Vector Store).
*   **Sortie :** Statut des composants.
*   **Exemple :**
    ```json
    {
      "status": "healthy",
      "services": {
        "database": "connected",
        "vector_store": "connected",
        "llm_provider": "reachable"
      }
    }
    ```

### `GET /dataset-status`
*   **Rôle :** Consulter l'état de fraîcheur des jeux de données.
*   **Sortie :** Liste des indicateurs avec date de dernière mise à jour.
*   **Exemple :**
    ```json
    [
      {"indicator": "GDP_GROWTH", "source": "World Bank", "last_update": "2023-12-01"},
      {"indicator": "USD_HTG_REF", "source": "BRH", "last_update": "2024-03-15"}
    ]
    ```

---

## 2. Endpoints AI & Conversationnels

### `POST /ask`
*   **Rôle :** Point d'entrée unique pour les questions en langage naturel (RAG + SQL).
*   **Payload Entrée :** `{"query": "Texte de la question", "stream": false}`
*   **Payload Sortie :**
    ```json
    {
      "answer": "La croissance d'Haïti...",
      "intent": "HYBRID",
      "data": { "table_markdown": "...", "points": [...] },
      "citations": [
        {"id": 1, "source": "BRH", "document": "Note 2023", "page": 12}
      ],
      "request_id": "uuid-..."
    }
    ```
*   **Validations :** Query non vide, max 500 caractères.

---

## 3. Endpoints de Données (Analytique)

### `GET /indicator-trend`
*   **Rôle :** Obtenir la série temporelle et la tendance d'un indicateur.
*   **Paramètres :** `indicator_code` (ex: `INFLATION`), `country_code` (ex: `HTI`), `period` (ex: `last_5_years`).
*   **Validation :** Codes ISO validés contre le référentiel.
*   **Sortie :**
    ```json
    {
      "series": [{"date": "2023-12-31", "value": 24.5}, ...],
      "analysis": {
        "trend": "DOWN",
        "cagr_3y": -1.2,
        "is_outlier_present": false
      }
    }
    ```

### `POST /compare`
*   **Rôle :** Générer une comparaison multi-pays sur un ou plusieurs indicateurs.
*   **Payload Entrée :** `{"indicators": ["GDP"], "countries": ["HTI", "DOM", "JAM"], "base_100": true}`
*   **Sortie :** Matrice de données alignée temporellement pour affichage graphique.

---

## 4. Endpoints Documentaires & Synthèse

### `GET /country-brief/{country}`
*   **Rôle :** Générer une fiche de synthèse "Executive Summary" d'un pays.
*   **Sortie :** Un bloc Markdown structuré contenant les indicateurs clés et le dernier contexte politique/économique issu des rapports.

### `GET /documents-search`
*   **Rôle :** Recherche sémantique pure dans la base documentaire (sans synthèse LLM).
*   **Paramètres :** `q` (texte), `source` (Optionnel), `year` (Optionnel).
*   **Sortie :** Liste des chunks les plus pertinents.

---

## 5. Endpoints de Métadonnées

### `GET /sources`
*   **Rôle :** Lister les sources d'information et leur score de fiabilité.
*   **Sortie :**
    ```json
    [
      {"id": "...", "name": "BRH", "reliability": 5, "type": "National"},
      {"id": "...", "name": "World Bank", "reliability": 5, "type": "International"}
    ]
    ```

---

## 6. Gestion des Erreurs Standards

| Code HTTP | Cause | Message Type |
| :--- | :--- | :--- |
| **400** | Paramètre invalide (ex: pays inexistant). | `INVALID_PARAMETER` |
| **404** | Ressource non trouvée. | `NOT_FOUND` |
| **429** | Limite de requêtes atteinte (Rate Limit). | `TOO_MANY_REQUESTS` |
| **500** | Erreur interne (DB down, Timeout LLM). | `INTERNAL_SERVER_ERROR` |
| **503** | Service en maintenance/surchargé. | `SERVICE_UNAVAILABLE` |

---

## 7. Recommandations de Développement

*   **Versionnage :** Inclure `/v1/` dans l'URL de base.
*   **Compression :** Activer Gzip pour les réponses `/compare` qui peuvent être lourdes.
*   **Timeout API :** Fixé à 30 secondes pour les routes `/ask` (RAG lourd) avec gestion du streaming en option.
*   **Sécurité :** CORS configuré, limitation par IP pour le MVP.
