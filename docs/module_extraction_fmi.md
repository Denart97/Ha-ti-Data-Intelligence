# Conception du Module d'Extraction : FMI (Fonds Monétaire International)

Ce document décrit la spécification technique du module d'extraction ciblant l'API REST du FMI, basée sur la norme SDMX. C'est un moteur plus complexe que celui de la Banque Mondiale en raison de la structure multidimensionnelle des données.

---

## 1. Identification des Datasets et Dataflows

L'API du FMI repose sur des **Dataflows** (flux de données). 
*   **Endpoint de découverte :** `GET http://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow`
*   **Dataflows prioritaires pour Haïti :**
    *   `IFS` (International Financial Statistics) : Taux d'intérêt, monnaie, change.
    *   `WEO` (World Economic Outlook) : Projections du PIB, dette, inflation.
    *   `DOT` (Direction of Trade Statistics) : Exportations/Importations par partenaire.
    *   `CPI` (Consumer Price Index) : Données d'inflation détaillées.

## 2. Construction des Requêtes (SDMX-JSON)

Les requêtes s'articulent autour d'une "Key" filtrant les dimensions (Fréquence, Zone, Indicateur).
*   **Structure de l'URL :** `CompactData/{DataflowID}/{Frequency}.{Country}.{Indicator}`
*   **Exemple (Taux du marché monétaire pour Haïti, Mensuel) :** 
    `GET http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.HT.FIMM_PA_NUM`
*   **Composants de la clé :**
    - `M` : Mensuel (ou `A` pour Annuel).
    - `HT` : Code pays IMF (Attention : le FMI utilise souvent ISO 2 caractères, parfois 3).
    - `FIMM_PA_NUM` : Code de l'indicateur dans la dimension.

## 3. Parsing des Réponses

Le flux SDMX-JSON est très imbriqué.
*   **Navigation :** La donnée se trouve généralement dans `DataSet.Series`.
*   **Observations :** Les valeurs sont dans l'attribut `Obs`.
*   **Règle métier :** Le parseur doit aplatir (flatten) cette structure récursive pour extraire un dictionnaire simple `{date: value}`.

## 4. Harmonisation des Métadonnées

*   **Pays :** Mapper le code 2-lettres (`HT`) vers notre ISO-3 (`HTI`).
*   **Indicateurs :** Utiliser une table de correspondance (`Indicator Map`) pour lier les codes IMF complexes (ex: `PCPI_PCH_PT`) vers nos codes taxonomie (ex: `INFLATION_GA`).

## 5. Gestion des Fréquences et Unités

*   **Fréquences :** L'API renvoie des formats type `2023-M03` ou `2023`. Le normalisateur doit convertir systématiquement en date de fin de période (`2023-03-31` ou `2023-12-31`).
*   **Unités :** Le FMI utilise souvent des multiplicateurs (`UNIT_MULT`). Si `UNIT_MULT` = 6, la valeur brute 15 doit être multipliée par 10^6 pour obtenir 15 000 000. C'est une étape critique avant insertion.

## 6. Intégration en Base Commune

L'insertion suit le même modèle que le module WB : **Bulk Upsert**.
- On utilise l'`indicateur_id`, `pays_id` et `date_valeur` comme clé d'unicité.
- Le `dataset_id` sera rattaché à la source "FMI - {Dataflow}".

## 7. Gestion des Révisions de Données

Le Fmi révise souvent les données historiques (particulièrement le WEO).
*   **Approche :** On écrase les valeurs existantes si la nouvelle version propose un chiffre différent pour la même période (`ON CONFLICT DO UPDATE`), car le dernier chiffre publié par le FMI est considéré comme le plus "vrai".

## 8. Journalisation (Logging)

*   **Identifiant de Dataflow :** Logger chaque flux traité.
*   **Metadata Check :** Logger si un nouvel indicateur est détecté mais non présent dans notre taxonomie.
*   **Performance :** Temps de réponse (le FMI est parfois lent).

## 9. Tests du Module

*   **Validation SDMX :** Tester le parseur avec un échantillon de JSON SDMX complexe (objets vides, séries multiples).
*   **Test de conversion d'unité :** Vérifier que `15` avec `UNIT_MULT: 6` devient bien `15,000,000`.
*   **Test de Robustesse :** Le FMI limite à 50 000 points par requête. Vérifier que nous ne dépassons pas ce seuil.

---

## 10. Architecture Python (Modules)

Le module sera logé dans `data_ingestion/sql_loaders/fmi/`.

1.  **`sdmx_client.py`** : Client HTTP bas niveau. Gère les URLs SDMX, les timeouts et les retries.
2.  **`catalog_manager.py`** : Gère la liste des Dataflows et des dimensions. Permet de "chercher" les codes indicateurs.
3.  **`parser.py`** : Transforme le JSON SDMX "CompactData" en liste d'objets standardisés (extraction des `Obs`).
4.  **`normalizer.py`** : Applique les conversions d'unités (`UNIT_MULT`) et de dates. Map les codes vers la taxonomie.
5.  **`main_fmi_etl.py`** : Le script principal qui itère sur les indicateurs configurés et pilote le flux.
