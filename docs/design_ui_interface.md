# Spécification Interface Utilisateur (UX/UI) : Haiti Data Intelligence

Ce document définit les principes de design, les composants et le parcours utilisateur pour la plateforme. L'objectif est de proposer une expérience **premium, sobre et orientée décision**.

---

## 1. Principes de Design & Identité Visuelle

*   **Esthétique :** "Digital Professionalism". Palette de couleurs inspirée des institutions financières (Bleu Nuit, Gris Ardoise, Or discret pour les accents).
*   **Typographie :** Utilisation de polices sans-serif modernes (ex: *Inter* pour le corps, *Outfit* pour les titres) pour une lisibilité maximale des chiffres.
*   **Mode :** Support natif du Dark Mode (fond `#0f172a`) et Light Mode (fond `#f8fafc`).
*   **Effets :** Glassmorphism discret pour les cartes de données, transitions fluides.

---

## 2. Parcours Utilisateur (User Journey)

1.  **Exploration (Landing) :** L'utilisateur arrive sur un tableau de bord global (Macro-Haiti) affichant les 4 indicateurs vitaux (Inflation, Taux de change, PIB, Réserves).
2.  **Interrogation (AI Chat) :** L'utilisateur pose une question complexe. Le système affiche la réponse textuelle à gauche et les données chiffrées/graphiques à droite.
3.  **Comparaison & Analyse :** En un clic, l'utilisateur bascule sur l'outil de comparaison pour situer Haïti par rapport à la République Dominicaine ou la Jamaïque.
4.  **Approfondissement (Sources) :** L'utilisateur survole une citation pour voir la source ou clique pour consulter le PDF original.
5.  **Dissémination (Briefing) :** L'utilisateur génère un résumé PDF exportable pour sa hiérarchie.

---

## 3. Composants Clés de l'Interface

### 3.1 La Sidebar (Navigation)
*   **Recherche Globale :** Barre de recherche persistante.
*   **Menus :** Dashboard Macro, Assistant Intelligent, Bibliothèque Documentaire, Comparateur.
*   **Status Indicators :** Témoins de connexion aux bases de données.

### 3.2 La Zone de Question-Réponse (Chat Interactif)
*   **Input :** Champ de saisie avec suggestions automatiques d'indicateurs.
*   **Réponse :** Format Markdown avec citations cliquables.
*   **Context Panel :** Panneau latéral droit affichant automatiquement un graphique Plotly lié à la réponse.

### 3.3 La Zone de Visualisation (Charts)
*   **Interactivité :** Tooltips détaillés, zoom sur les séries temporelles, export d'images.
*   **Types :** Multi-line charts (comparaisons), Bar charts (distributions), Heatmaps (géographie).

### 3.4 Le Panneau des Sources (Audit Trail)
*   **Provenance :** Liste des documents sources avec badges de fiabilité.
*   **PDF Viewer :** Aperçu du document intégré pour ne pas quitter l'application.

---

## 4. Hiérarchie Visuelle & Ergonomie

1.  **Niveau 1 (Focus) :** Les chiffres clés (Hero metrics) en gras et grande taille.
2.  **Niveau 2 (Analyse) :** Les graphiques de tendance.
3.  **Niveau 3 (Preuve) :** Les citations et notes méthodologiques en fond de page ou panneau secondaire.

**Recommandation Ergonomique :** "Don't make me calculation". L'interface doit afficher directement les Deltas (ex: *+1.2% vs mois dernier*) plutôt que de laisser l'utilisateur faire la soustraction mentalement.

---

## 5. États du Système (Feedback)

### 5.1 Chargement (Loading States)
*   **Skeletton Screens :** Affichage de blocs grisés pulsant pendant le chargement des graphiques.
*   **AI Streaming :** La réponse du chat s'affiche mot par mot pour réduire la perception de latence du LLM.

### 5.2 Erreurs & Cas Limites
*   **Empty State :** Message clair si aucune donnée n'est trouvée pour une période donnée, avec suggestion d'une période alternative.
*   **API Error :** Bannière discrète en haut de l'écran avec bouton "Réessayer".

---

## 6. Niveau d'Information par Profil

*   **Décideur (Vue High-level) :** Chiffres clairs, tendances, conclusions du briefing.
*   **Analyste (Vue Deep-dive) :** Accès aux données brutes (JSON/CSV), méthodologies détaillées, comparaison multi-sources.

---

## 7. Maquette Logique (Mockup Structure)

```text
+-------------------------------------------------------------+
| [ Logo ]   [ Recherche... ]                     [ Profil ]  |
+-------------------------------------------------------------+
| MENU        |                                               |
| - Dashboard |  Dernières Tendances (Haiti)                  |
| - Chat AI   |  +------------+ +------------+ +------------+ |
| - Comparer  |  | Inflation  | | Taux Chg. | | PIB       | |
| - Docs      |  | 24.5% [^]  | | 132.5 [v]  | | -1.2% [v] | |
|             |  +------------+ +------------+ +------------+ |
|             |                                               |
|             |  Analyse Assistée                             |
|             |  +--------------------------+  +-----------+  |
|             |  | Question: "Pourquoi..."  |  | [ Graph ] |  |
|             |  |                          |  | [ Plotly] |  |
|             |  | Réponse AI: "En raison.. |  | [       ] |  |
|             |  | [Source 1] [Source 2]    |  |           |  |
|             |  +--------------------------+  +-----------+  |
+-------------+-----------------------------------------------+
```
