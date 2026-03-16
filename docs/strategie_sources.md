# Stratégie de Sélection des Sources : Haiti Data Intelligence

Ce document définit la politique de gouvernance des données. Il permet de garantir la fiabilité ("Grounded Truth") essentielle à une plateforme d'intelligence économique et de limiter les hallucinations du RAG en contrôlant strictement le corpus ingéré.

---

## 1. Critères d'Évaluation et de Sélection

### 1.1 Critères d'Inclusion (Facteurs Clés)
- **Autorité & Légitimité :** L'institution émettrice est-elle mandatée officiellement pour produire cette donnée ? (ex: IHSI pour l'inflation, BRH pour la monnaie).
- **Régularité de Publication :** La source publie-t-elle à des intervalles prévisibles (mensuel, trimestriel, annuel) ?
- **Méthodologie Transparente :** Les notes méthodologiques sont-elles accessibles ?
- **Stabilité Structurelle :** Pour les rapports PDF, la structure (titres, tableaux) est-elle relativement constante d'une publication à l'autre pour faciliter le parsing ?

### 1.2 Critères de Qualité (Scoring sur 10)
Chaque source est évaluée selon 4 dimensions :
1. **Poids Institutionnel (3 pts) :** Officielle/Internationale (3), Privé Reconnu (2), Autre (1).
2. **Accessibilité Technique (3 pts) :** API native/CSV direct (3), PDF structuré/Scraping facile (2), PDF scanné/image non-OCR (0).
3. **Fréquence de Mise à Jour (2 pts) :** Mensuelle/Temps Réel (2), Annuelle (1), Irrégulière (0).
4. **Profondeur Historique (2 pts) :** > 10 ans (2), 5-10 ans (1), < 5 ans (0).

### 1.3 Critères d'Exclusion (No-Go)
- **Opinion / Editorial pur :** Sites d'opinion politique sans données chiffrées vérifiables.
- **Rumeurs réseaux sociaux :** Même très relayées, interdiction formelle d'ingérer des posts X/WhatsApp dans le moteur RAG B2B.
- **PDF Scannés d'anciennes qualités :** Si l'OCR (Optical Character Recognition) fait trop d'erreurs, exclusion de l'intégration vectorielle pour le MVP afin d'éviter la corruption sémantique.
- **Micro-Sondages non représentatifs :** Études portant sur un échantillon trop faible sans redressement statistique.

---

## 2. Tableau de Priorisation des Sources

### 2.1 Sources Structurées (Dashboard Quantitatif)

| Institution / Source | Domaine Principal | Score | Statut | Recommandation d'Usage (MVP / V2) |
| :--- | :--- | :--- | :--- | :--- |
| **World Bank Open Data** | Macro globale, Comparatifs RD/CARICOM | **10** (API) | **Primaire** | MVP : Source n°1 pour les comparaisons. API très stable (REST/Python wbdata). |
| **BRH (Banque Centrale)** | Monnaie, Réserves, Change | **8** (Excel/Web) | **Primaire** | MVP : Indicateurs financiers quotidiens/mensuels. Extraction via scripts Python réguliers. |
| **IHSI (Inst. de Statistique)** | Inflation (IPC), PIB local | **7** (PDF/Web) | **Primaire** | MVP : Source officielle de l'inflation. Extraction Excel/PDF (tabula-py) requise. |
| FMI (IMF Data) | Dette, Macro projections | **9** (API/Excel) | Secondaire | V2 : Pour compléter ou recouper les chiffres de la Banque Mondiale. |
| OMD (Observatoire Marché) | Prix des denrées alimentaires | **6** (PDF) | Secondaire | V2 : Granularité intéressante (surveillance de la faim) mais scraping fastidieux. |

### 2.2 Sources Documentaires (Moteur RAG - IA)

| Institution / Document | Type de Contenu | Score | Statut | Recommandation d'Usage (MVP / V2) |
| :--- | :--- | :--- | :--- | :--- |
| **BRH - Notes Polit. Monétaire** | Analyse de conjoncture | **9** (PDF propres) | **Primaire** | MVP : Ingestion complète. Cœur du raisonnement sur l'inflation et le change. |
| **Banque Mondiale / FMI (Art IV)** | Évaluations risque-pays (Haiti) | **10** (PDF text) | **Primaire** | MVP : Ingestion complète pour le point de vue international. Très structuré. |
| **Le Moniteur (Journal Officiel)** | Décrets, Lois Organiques | **6** (Scans/PDF) | Secondaire | V2 : Extrêmement utile pour la "Compliance" légale, mais OCR souvent très lent et complexe. |
| **Ministère de l'Économie (MEF)** | Exécution budgétaire | **7** (PDF mensuel)| Secondaire | V2 : À inclure une fois le pipeline de parsing tabulaire PDF stabilisé. |
| **Presse Éco (Le Nouvelliste)** | Interviews, chroniques éco | **6** (Web) | Secondaire | V2 : Nécessite un filtre "Opinion" vs "Cahier Économique". Ne pas mélanger avec la vérité officielle. |

### 2.3 Sources Géographiques & Cartographiques (V2/V3)
*(À intégrer pour les futures visualisations de cartes)*
- **CNIGS (Centre National Info Géo-Spatiale)** : Limites administratives, Shapefiles officiels (Primaire).
- **HOTOSM / OCHA** : Infrastructures, points d'eau post-désastre (Secondaires).

### 2.4 Sources de Veille (V3/Alerting)
- **ReliefWeb (UN)** : Fil RSS pour les "Updates" immédiats sur les situations humanitaires (Catastrophes naturelles, blocages).

---

## 3. Stratégie de Gouvernance des Sources

### 3.1 Gérer les Contradictions ("Truth Conflict")
Il arrive que l'IHSI, la BRH et la Banque Mondiale affichent trois chiffres légèrement différents pour le PIB d'une même année (différence de base, d'année fiscale vs calendaire).
*   **Règle d'or du Produit :** Toujours afficher la source internationale (Banque Mondiale) pour les *Comparaisons inter-pays*, mais privilégier les sources nationales (IHSI/BRH) pour les *Analyses internes spécifiques à Haïti*.
*   **Prompting RAG :** Indiquer explicitement au LLM de préciser l'organe émetteur : *"Selon l'IHSI, l'inflation est de X%, tandis que le FMI projetait Y%..."*.

### 3.2 Cycle de Vie de la Donnée
1.  **Audits Trimestriels :** Vérifier que les sites de la BRH/IHSI n'ont pas changé d'URL ou de format (risque majeur de bris de pipeline ETL).
2.  **Versioning de l'Index Vectoriel :** Le RAG ne supprime jamais d'anciens documents mais les flag avec l'année. Exemple : Privilégier un chunk de l'année 2024 plutôt que 2021 lors de la recherche vectorielle (Re-ranking par Metadata de date).
3.  **Traçabilité absolue (Data Lineage) :** Toute valeur numérique dans le Dashboard et toute phrase RAG doit stocker deux métadonnées en arrière-plan : `Source_ID` et `Date_Ingestion`.
