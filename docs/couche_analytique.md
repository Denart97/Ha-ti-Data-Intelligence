# Couche Analytique : Haiti Data Intelligence

Ce document définit la logique métier du moteur analytique (le "Stats Engine") situé dans le backend. Ce module transforme les données brutes de la base de données en indicateurs intelligibles et prêts pour la visualisation.

---

## 1. Fonctions Analytiques Principales

### 1.1 Calcul des Évolutions Temporelles (`calculate_growth`)
*   **Rôle :** Calculer le taux de variation d'un indicateur sur une période.
*   **Entrées :** `series: List[DataPoint]`, `type: 'YoY' | 'MoM'`.
*   **Règle :** `((V_t / V_{t-n}) - 1) * 100` où `n` est le pas (12 pour YoY mensuel, 1 pour YoY annuel).
*   **Sortie :** `TimeSeriesResult` avec valeurs exprimées en pourcentage.

### 1.2 Comparaisons Multi-Pays (`compare_series`)
*   **Rôle :** Aligner plusieurs séries de pays différents sur une même base temporelle.
*   **Entrées :** `list_of_series: List[List[DataPoint]]`, `base_year: Optional[int]`.
*   **Règle :** 
    - Indexation (Base 100) optionnelle : `(V_t / V_{base_year}) * 100`.
    - Harmonisation des fréquences (Upsampling/Downsampling) si nécessaire.
*   **Sortie :** `MatrixResult` (Tableau croisé par date et pays).

### 1.3 Détection de Tendances (`detect_trend`)
*   **Rôle :** Identifier si une série est en phase d'accélération, de ralentissement ou de stagnation.
*   **Entrées :** `series: List[DataPoint]`, `window: int` (ex: 3 pour une moyenne mobile sur 3 mois).
*   **Règles :**
    - Calcul de la **Moyenne Mobile**.
    - Calcul de la **Pente (Slope)** via régression linéaire simple sur les `N` derniers points.
*   **Sortie :** `TrendLabel` ('UP', 'DOWN', 'STABLE') et `ConfidenceInterval`.

### 1.4 Résumé de Séries (`compute_summary`)
*   **Rôle :** Produire des statistiques descriptives pour le RAG ou les tooltips.
*   **Entrées :** `series: List[DataPoint]`.
*   **Règles :** Calcul du `Min`, `Max`, `Moyenne`, `Médiane`, `Écart-type` (Volatility) et `CAGR` (Compound Annual Growth Rate).
*   **Sortie :** `SummaryStatsObject`.

### 1.5 Préparation des Visualisations (`prepare_chart_data`)
*   **Rôle :** Formater les données pour Plotly (Frontend).
*   **Entrées :** `processed_data: Any`, `chart_type: 'LINE' | 'BAR' | 'PIE'`.
*   **Règles :** 
    - Tri chronologique obligatoire.
    - Remplacement des `NaN` par `null` (JSON standard).
    - Ajout de labels (`Nom de l'indicateur`, `Unité`).
*   **Sortie :** `JSON-Plotly-Friendly`.

---

## 2. Garde-fous Qualité & Validation

| Risque | Garde-fou Analytique |
| :--- | :--- |
| **Division par zéro** | Si `V_{t-n} == 0`, retourner `null` et marquer un flag `ERR_DIV_ZERO`. |
| **Séries trop courtes** | Minimum de 2 points pour une croissance, 5 points pour une tendance. Sinon, renvoyer `INSUIFFICIENT_DATA`. |
| **Outliers massifs** | Algorithme de détection (Z-score > 3). Si détecté, la valeur est conservée mais le `Summary` ajoute une note : "Potential Outlier detected". |
| **Unités incohérentes** | Blocage du calcul si on tente de comparer des Gourdes (HTG) et des Dollars (USD) sans conversion préalable. |

---

## 3. Gestion des Cas Limites (Edge Cases)

1.  **Données Manquantes (Gaps) :**
    - Si un mois manque au milieu d'une série : Ne pas calculer le taux de croissance pour ce mois spécifique. Ne pas "inventer" de données par défaut.
2.  **Changement de base (Rebasing) :**
    - Cas fréquent à l'IHSI (PIB base 1986 vs 2012). Le moteur doit être capable d'identifier la rupture de série via les métadonnées et d'afficher un avertissement à l'utilisateur : *"Attention : Changement de méthodologie source en [Année]"*.
3.  **Échelles disproporionnées :**
    - Si on compare le PIB d'Haïti et des USA sur un même axe : Proposer automatiquement une **échelle logarithmique** ou un **indice base 100** pour rendre le graphique lisible.

---

## 4. Architecture du Code (Spécification `stats_calc.py`)

*   **`SeriesProcessor` (Classe) :**
    - `clean()`: Gère les types et les valeurs aberrantes.
    - `transform()`: Applique les calculs (Growth, Rolling, etc.).
    - `summarize()`: Génère les métriques descriptives.
*   **`Comparator` (Classe) :**
    - `align_dates()`: Jointure de plusieurs pays sur un index temporel commun.
    - `normalize()`: Mise en base 100.
