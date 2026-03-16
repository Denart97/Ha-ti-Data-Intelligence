# Système de Citations et Traçabilité : Haiti Data Intelligence

Ce document définit les mécanismes permettant de garantir la vérifiabilité de chaque information fournie par la plateforme, un impératif pour une crédibilité B2B auprès des décideurs économiques.

---

## 1. Format et Niveau de Détail des Citations

Les citations ne sont pas de simples notes de bas de page ; elles sont intégrées au flux de lecture pour permettre une vérification instantanée.

### 1.1 Format dans le texte
*   **Notation :** Utilisation de crochets numérotés `[n]` immédiatement après l'affirmation ou le chiffre.
*   **Interaction :** Cliquer sur `[n]` doit mettre en évidence (highlight) la source dans le panneau latéral ou ouvrir le document source à la page exacte.

### 1.2 Niveau de détail du bloc de référence
Chaque référence en fin de réponse doit afficher :
*   **Identifiant :** `[n]`
*   **Titre court :** Ex: *Rapport Annuel BRH 2022*.
*   **Localisation précise :** Page(s) X, Paragraphe Y (si disponible via le parsing).
*   **Date :** Date de publication du document.
*   **Lien :** URL directe vers le PDF ou le dataset original.

---

## 2. Hiérarchie des Sources (Lineage B2B)

Toutes les sources n'ont pas le même poids. Le système doit distinguer la nature de la preuve.

| Type de Source | Définition | Affichage UI |
| :--- | :--- | :--- |
| **Primaire** | Source officielle émettrice (BRH, IHSI, Banque Mondiale, FMI). | Badge "Source Officielle" / "Autorité". |
| **Secondaire** | Rapports d'analyse, articles de presse spécialisée, études académiques. | Badge "Analyse Tierce" / "Contexte". |
| **Donnée Calculée**| Résultat d'une agrégation ou d'un calcul HDI (ex: Moyenne 3 ans). | Mention "Calculé par Haiti Data Intelligence". |

---

## 3. Gestion des Dates et Fraîcheur

La crédibilité dépend de la précision temporelle.
*   **Date de publication :** Date à laquelle la source a été émise.
*   **Date de capture (Ingestion) :** Indiquée systématiquement pour les pages web (Scraping) pour prouver l'état de la source au moment de la lecture.
*   **Alerte Obsolescence :** Si une citation provient d'un document vieux de plus de 2 ans alors qu'un nouveau cycle de données est passé, l'IA ajoute une mention : *"Note : Cette information provient d'une archive historique [2021]"*.

---

## 4. Métadonnées Affichables (Tooltip & Side Panel)

Au survol d'une citation, une "Info-bulle" affiche les métadonnées critiques :
- **Institution :** Logo + Nom.
- **Fiabilité :** Note de 0 à 5 étoiles (basée sur le `reliability_score`).
- **Extrait :** Les 150 premiers caractères du chunk original pour confirmer le contexte sans changer de page.

---

## 5. Gestion des Citations Multiples

Si une information est corroborée par plusieurs sources :
*   **Format :** `[1, 2, 4]`.
*   **Logique de Fusion :** Le moteur de génération doit privilégier la source primaire dans le texte, mais lister toutes les sources concordantes en référence pour renforcer la preuve.
*   **Conflit :** En cas de contradiction, le moteur utilise le format : *"La BRH indique X [1], tandis que le FMI estime Y [2]"*.

---

## 6. Traçabilité Réponse ↔ Document ↔ Donnée Structurée

Le système maintient un "Lignage" technique (Data Lineage) invisible mais auditable.

*   **Identifiant Unique de Réponse (Request ID) :** Chaque interaction génère un ID permettant de retrouver dans les logs :
    - La query SQL exécutée.
    - Les UUIDs des chunks ChromaDB récupérés.
    - La température du LLM au moment de la synthèse.
*   **Lien SQL-RAG :** Si un graphique est affiché à côté d'une analyse textuelle, ils partagent un lien de traçabilité d'indicateur commun (`indicator_id`), garantissant que le texte commente bien la donnée visualisée.

---

## 7. Architecture Technique (Implémentation)

1.  **Table `citations` :** Table de jointure dans PostgreSQL reliant `briefing_id` et `chunk_id`.
2.  **Module `citation_handler.py` :**
    - Fonction `format_citation_list()` : Prend les IDs de chunks et génère les blocs de références formatés.
    - Fonction `get_source_badge()` : Attribue le niveau de priorité (Primaire/Secondaire).
3.  **Frontend Interface :** Panneau escamotable "Sources & Méthodologie" à droite de chaque réponse chat.
