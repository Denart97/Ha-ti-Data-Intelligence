# Stratégie de Gouvernance des Données : Haiti Data Intelligence

Ce document définit les principes et processus pour assurer la confiance, la qualité et la traçabilité des données tout au long de leur cycle de vie au sein de la plateforme.

---

## 1. Principes Fondamentaux de Gouvernance

### 1.1 Règles de Qualité (Data Quality Rules)
Chaque donnée ingérée doit satisfaire aux règles suivantes :
*   **Complétude (Completeness) :** Toute métrique introduite doit avoir un `pays_id`, un `indicateur_id`, une `date_valeur` et une valeur numérique valide (ou NULL explicite).
*   **Cohérence (Consistency) :** Les formats de dates et de devises doivent respecter la norme définie (ex: les taux d'inflation stockés en décimal, affichés en %).
*   **Exactitude (Accuracy) :** La donnée dans notre base doit être *mathématiquement identique* à la donnée source publiée. Aucune transformation altérant la valeur (ex: arrondis brutaux) ne doit survenir lors de l'ETL sans documentation.

### 1.2 Contrôle de Fraîcheur (Data Freshness Monitoring)
*   **SLA de Fraîcheur :** Les données mensuelles (ex: inflation IHSI) doivent être disponibles sur la plateforme au maximum **72h** après leur publication officielle.
*   **Mise en œuvre :** Le cron job ETL vérifie quotidiennement la date de dernière mise à jour (`last_updated_at` dans la table `datasets`).
*   **Dashboard Interne :** Un tableau de bord technique (Monitoring) affiche en rouge les datasets n'ayant pas reçu de mise à jour depuis plus longtemps que leur fréquence théorique (ex: Data annuelle avec `last_updated_at` > 18 mois).

### 1.3 Traçabilité (Data Lineage)
*   Aucune donnée ne peut exister sans un "Père". Toute ligne dans `valeurs_indicateurs` est rattachée à un `dataset_id`.
*   Toute réponse RAG est rattachée par clé étrangère à un `chunk_id` et un `document_id`.
*   Un changement manuel (correction d'une erreur de scraping) doit être enregistré dans une table de logs applicatifs : `[Heure] [Admin_ID] changed [Valeur] from X to Y for [Indicateur_ID] (Reason: Corrected OCR error)`.

## 2. Gestion des Anomalies et Incohérences

### 2.1 Gestion des données contradictoires (Conflits Multi-Sources)
*   **Règle du Conservatisme :** Haïti est un marché où les chiffres officiels (IHSI) et institutionnels (Banque Mondiale, CEPALC) diffèrent souvent. On stocke les deux sans en écraser aucun.
*   **Moteur de Résolution :** En l'absence de filtre explicite de l'utilisateur sur le Dashboard, la hiérarchie par défaut (Fallback) pour l'affichage est :
    1. Base de données internationale agréée (World Bank) *pour sa méthodologie standardisée*.
    2. Base nationale source (IHSI / BRH).
    3. Autre (FMI).

### 2.2 Calcul du Score de Fiabilité (Reliability Scoring)
Le score de fiabilité (sur 100) affiché sur un graphique est dynamique :
*   Base Score Institutionnel (ex: Banque Mondiale = 90/100, Article de Presse = 40/100).
*   *- 10 points* si la série contient plus de 15% de valeurs manquantes (NULL).
*   *- 20 points* si la source n'a plus été mise à jour depuis plus de 2 cycles complets (ex: donnée mensuelle pas à jour depuis 2 mois).

## 3. Gestion des Mises à Jour (Data Lifecycle)

### 3.1 Stratégie de Mise à Jour (Append-Only vs Overwrite)
*   **Données Structurées :** "Soft Overwrite". Une donnée existante avec même clé `(indicateur, pays, date, source)` est écrasée (Update) par une nouvelle ingestion de la même source *uniquement* si la valeur change (les instituts révisent souvent leurs chiffres a posteriori).
*   **Documents / RAG :** "Append-Only strict". Un document PDF n'est jamais modifié. S'il y a un erratum publié par la BRH, le nouveau PDF est indexé séparément. L'IA précisera : "Le document d'erratum du X indique...".

### 3.2 Politique de Conservation des Historiques (Retention Policy)
*   **Séries Temporelles (SQL) :** Stockage perpétuel ("Cold-Forever"). L'historique (50/60 ans) est très léger en SQL (quelques Ko) et précieux.
*   **Vecteurs RAG (ChromaDB) :** Conservation perpétuelle des index, MAIS on applique un filtre d'obsolescence (`recency bias`) dans la recherche : Les chunks vieux de plus de 5 ans perdent du poids sémantique au profit des chunks récents, sauf si la question demande explicitement une donnée "historique".
*   **Logs Applicatifs :** Traces conservées pendant 1 an, puis archivées (S3/Glacier).

## 4. Documentation Interne des Datasets (Data Catalog)
*   **Outil :** Chaque jeu de données de la DB doit être documenté dans la table `indicateurs` et dans le dictionnaire métier (`taxonomie_metier.md`).
*   **Champs obligatoires du Dictionnaire :** Nom, Code, Unité, Origine, Note Méthodologique de la source (ex: "L'IHSI a changé l'année de base de l'IPC en 2017. Rupture de série potentielle.").
*   Cet inventaire est vital pour le prompt LLM et pour les Analysts Data qui rejoindront le projet.

---

## 5. Checklist Qualité (À appliquer à chaque NOUVELLE Source)

Avant d'intégrer un nouveau site Web ou API dans le pipeline ETL de "Haiti Data Intelligence", l'analyste/dev doit valider les points suivants :

### A. Évaluation Métier
- [ ] La source est-elle reconnue / officielle (vs un blog ou un tweet) ?
- [ ] Le type de donnée publié répond-il à un des besoins du Produit (Macro, Pauvreté, etc.) ?
- [ ] Existe-t-il une autre source plus réputée fournissant déjà ce chiffre ?

### B. Évaluation Technique (ETL)
- [ ] Le format de données est-il programmable de manière robuste (API JSON, fichier CSV standard, PDF vectoriel avec texte extractible) ?
- [ ] Les PDF (si document) sont-ils traités par OCR ou sont-ils juste des images ? (Rejet si image pure sans OCR fiable possible).
- [ ] Le lien de téléchargement / Endpoint est-il stable dans le temps (ou change-t-il à chaque mois) ?

### C. Normalisation & Mapping
- [ ] Ai-je documenté précisément l'unité de mesure d'origine (Gourdes, USD, milliers d'USD) ?
- [ ] Le mapping des concepts de la source vers la "taxonomie_metier.md" standardisée est-il définitif et testé ?
- [ ] Le script d'ingestion contient-il des blocs `try/except` avec logging et notification en cas de plantage ?
