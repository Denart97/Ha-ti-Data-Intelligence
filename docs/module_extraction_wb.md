# Conception du Module d'Extraction : Banque Mondiale (World Bank)

Ce document décrit la spécification technique du premier module Extracteur ("Data Fetcher") du projet Haiti Data Intelligence, ciblant l'API REST publique de la Banque Mondiale.

---

## 1. Endpoints Utiles

L'API de la Banque Mondiale (v2) est RESTful. Voici les endpoints critiques pour notre système :
*   **Données par Indicateur (Core Endpoint) :** 
    `GET http://api.worldbank.org/v2/country/{country_id}/indicator/{indicator_id}`
    *Permet d'obtenir la série temporelle d'un indicateur pour un pays précis.*
*   **Métadonnées Indicateurs :** 
    `GET http://api.worldbank.org/v2/indicator/{indicator_id}`
    *Permet de récupérer la définition et l'unité de mesure exacte si la taxonomie doit être mise à jour.*
*   **Métadonnées Pays :**
    `GET http://api.worldbank.org/v2/country/{country_id}`

## 2. Structure des Appels

*   **Format de réponse :** Forcé obligatoirement en JSON en ajoutant le query param `?format=json`.
*   **Filtre temporel :** Paramètre `date=Y1:Y2` (ex: `date=2000:2023`) pour limiter le payload et accélérer l'ETL (Delta Load).
*   **Exemple d'appel complet :** 
    `GET http://api.worldbank.org/v2/country/hti/indicator/NY.GDP.MKTP.CD?format=json&date=2010:2023&per_page=100`

## 3. Stratégie de Récupération (Indicateurs Haïti)

1.  **Boucle sur Taxonomie :** Le script lit la table PostgreSQL `indicateurs` pour récupérer la liste des codes API World Bank (ex: `FP.CPI.TOTL.ZG` pour l'inflation).
2.  **Exécution Paramétrée :** Pour chaque code, le script fait un appel avec `{country_id} = 'hti'`.
3.  **Filtrage Annuel (Delta Load) :** Avant l'appel, le script requête la base `valeurs_indicateurs` pour trouver la dernière année `last_date` insérée pour cet indicateur/pays. L'appel API demande uniquement de `last_date` à `Année_En_Cours` pour économiser la bande passante.

## 4. Stratégie de Récupération (Pays Comparateurs)

*   **L'astuce de l'API :** L'API World Bank permet de passer plusieurs codes ISO3 séparés par des point-virgules pour faire un seul appel groupé.
*   **Implémentation :** `{country_id} = 'hti;dom;jam;cub'` (Haïti + Rép. Dominicaine + Jamaïque + Cuba).
*   **Avantage :** Division par 4 du nombre de requêtes HTTP transmises, réduisant drastiquement le risque de blocage `RateLimit`.

## 5. Gestion de la Pagination

L'API renvoie les résultats sous forme d'une liste de 2 éléments. L'élément `[0]` contient les métadonnées de pagination, l'élément `[1]` contient un tableau d'objets data.
*   **Règle :** Par défaut, l'API renvoie 50 résultats.
*   **Optimisation :** Forcer `per_page=1000` dans l'URL. Vu qu'une série macro d'un pays compte rarement plus de 60 ans, un appel avec `per_page=1000` ou `per_page=5000` garantit de tout récupérer en une seule page (Single Fetch), évitant la complexité de coder un générateur de boucles `while page < pages`.

## 6. Gestion des Erreurs & Résilience

*   **Timeout :** Paramétré à `10 secondes`.
*   **Rate Limits / HTTP 429 :** La Banque Mondiale bloque temporairement les IP agressives.
*   **Implémentation :** Utilisation de la librairie `tenacity` en Python.
    ```python
    @retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(5))
    def _fetch_wb_data(...):
    ```
*   **Erreur 404 / Indicateur Invalide :** Logguée comme "WARNING" et Bypass (le script continue sur l'indicateur suivant sans planter globalement).

## 7. Normalisation des Réponses

La Banque Mondiale renvoie ce JSON asynchrone :
`[{"page":1,...}, [{"indicator": {"id":"NY.GDP..."}, "country": {"id":"HT"}, "value": 15000000, "date": "2023"}]]`

*   **Mapping Pydantic (Extracteur -> Standard Internal) :**
    1.  `date` ("2023") -> Convertie en `DATE` stricte ("2023-12-31" si fréquence annuelle, "2023-MM-LD" si mensuelle).
    2.  `country.id` ("HT") -> Converti en `pays_id` (UUID local) correspondant à ISO3 "HTI" via la table `pays`.
    3.  `indicator.id` -> Converti en `indicateur_id` (UUID local) via table de correspondance.
    4.  `value` -> Remplacer `null` de l'API JSON par `None` Python, converti en `NULL` PostgreSQL. Casté en `float`.

## 8. Insertion Temporaire & Base PostgreSQL

*   **Zone de Transit (Memory) :** Les données lues sont concaténées dans un DataFrame `Pandas` ou une liste de dictionnaires.
*   **Query SQL (Bulk Upsert) :**
    Pour éviter les doublons lors des exécutions répétées :
    ```sql
    INSERT INTO valeurs_indicateurs (indicateur_id, pays_id, date_valeur, dataset_id, valeur_numerique, statut)
    VALUES %s
    ON CONFLICT (indicateur_id, pays_id, date_valeur) 
    DO UPDATE SET 
        valeur_numerique = EXCLUDED.valeur_numerique,
        statut = EXCLUDED.statut,
        last_updated_at = NOW()
    WHERE valeurs_indicateurs.valeur_numerique IS DISTINCT FROM EXCLUDED.valeur_numerique;
    ```
    *Note : Ne met à jour que si les experts de la Banque Mondiale ont révisé le chiffre.*

## 9. Les Logs à Prévoir (Observabilité)

*   **Début de l'ETL :** `INFO: Démarrage extraction Banque Mondiale pour 15 indicateurs et 4 pays.`
*   **Pendant (Réseau) :** `DEBUG: Fetching URL http://... [Status 200, 450ms]`
*   **Statistiques (Fin) :** `INFO: Extraction WB terminée. 250 records fetchés. 10 lignes insérées. 240 ignorées (déjà à jour). 0 Erreurs.`
*   **Erreur Critique :** `CRITICAL: Le endpoint de la Banque mondiale rejette la connexion après 5 tentatives. Abandon de la tâche.`

## 10. Les Tests Minimum à Prévoir (Pytest)

*   `test_fetch_response_format()` : "Mocker" (`responses` ou `httpx-mock`) un faux JSON API WB et vérifier que notre parseur l'extrait sans erreur.
*   `test_handle_null_values()` : Fournir un JSON où `"value": null` et vérifier que le DataFrame génère un `pd.NA` ou le SQL un `NULL`, sans crasher ni insérer `0`.
*   `test_pagination_override()` : Vérifier que l'URL générée contient bien toujours `per_page=1000`.
*   `test_retry_mechanism()` : Mocker un échec 500 sur les 2 premiers appels et un 200 sur le 3ème, vérifier que la fonction réussit finalement.

---

## 11. Proposition d'Architecture Fichier par Fichier

Le code de ce module n'est pas un script unique de 500 lignes, mais découpé proprement dans `data_ingestion/sql_loaders/wb/` :

1.  **`client.py` (L'Acheteur) :**
    - Rôle : Gère purement le HTTP. Crée les requêtes GET, injecte `per_page`, implémente la logique de Retries (`@retry`). Ne connait rien à la base de données ou à la sémantique de l'indicateur.
2.  **`normalizer.py` (Le Traducteur) :**
    - Rôle : Reçoit le JSON brut de `client.py`. Contient les classes Pydantic. Transforme `"HT"` en `"HTI"`, corrige les dates, gère les conversions de devises si elles sont hardcodées, gère les valeurs nulles. Renvoie une liste propre d'objets `PointDeDonnee`.
3.  **`loader.py` (Le Magasinier) :**
    - Rôle : Prend la liste standardisée, ouvre une transaction SQLAlchemy vers PostgreSQL et exécute la commande `ON CONFLICT DO UPDATE`. S'assure que si la base plante, l'insertion s'annule (Rollback).
4.  **`main_wb_etl.py` (Le Chef d'Orchestre) :**
    - Rôle : Point d'entrée du Cron Job. Récupère la liste des pays (`HTI, DOM`) et indicateurs depuis le module Core. Fait une boucle, appelle `client` -> `normalizer` -> `loader`, et écrit le rapport de `Logs` final.
