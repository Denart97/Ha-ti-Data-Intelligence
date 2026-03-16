# Stratégie de Traitement des Données : Approche Hybride

Ce document définit l'architecture conceptuelle de traitement et de requêtage des données pour "Haiti Data Intelligence". Il décrit comment le système orchestre les requêtes de l'utilisateur vers les bonnes sources (Structurées vs Non-Structurées) et comment il garantit des réponses fiables et sourcées.

---

## 1. Architecture Conceptuelle : Le Routage Intelligent (Orchestrator)

L'application repose sur un **Routeur d'Intention (LLM Router)** en entrée. Lorsqu'un utilisateur pose une question, le LLM-Router analyse la requête et décide du / des moteurs à solliciter :
1.  **Moteur Quantitatif (Data Structurées / SQL)** : Pour les questions statistiques précises.
2.  **Moteur Qualitatif (RAG Documentaire / Vectoriel)** : Pour les questions d'analyse, de contexte ou de politique.
3.  **Synthèse Hybride** : Pour les requêtes complexes nécessitant à la fois le chiffre et l'explication.

---

## 2. Typologie des Questions et Routage

### 2.1 Requêtes strictement 100% Data Structurée
- **Définition :** Questions demandant une valeur numérique exacte, une évolution historique brute ou une comparaison chiffrée.
- **Exemples :** 
  - *"Quel était le de PIB d'Haïti en 2022 ?"* 
  - *"Montre-moi l'évolution de l'inflation entre 2018 et 2023."*
- **Traitement :** Le LLM-Router génère une requête SQL (Text-to-SQL) ou utilise une API prédéfinie pour interroger la base relationnelle (ex: PostgreSQL). Il renvoie un JSON qui est traduit par le Frontend en un graphique ou un tableau dynamique, accompagné d'une phrase courte ("Le PIB était de X milliards en 2022"). **Pas de RAG ici.**

### 2.2 Requêtes strictement Documentaires (Moteur RAG)
- **Définition :** Questions ouvertes appelant à comprendre des politiques, des facteurs qualitatifs, des opinions institutionnelles ou des résumés de textes.
- **Exemples :** 
  - *"Quelles sont les causes de la hausse de l'inflation au 3e trimestre selon la BRH ?"*
  - *"Quelles recommandations la Banque Mondiale fait-elle sur l'éducation ?"*
- **Traitement :** Le Router envoie la requête à la base de données vectorielle (RAG). L'algorithme de recherche (Semantic Search + Keyword via `taxonomie_metier.md`) trouve les 5 meilleurs extraits de rapports ("Chunks"). Le LLM final assemble ces chunks pour formuler la réponse narrative.

### 2.3 Requêtes Hybrides (Le "Saint-Graal")
- **Définition :** Requêtes nécessitant le chiffre exact *et* son explication contextuelle. C'est l'avenir (V2) de la plateforme.
- **Exemples :** 
  - *"Pourquoi le taux de change s'est-il autant dégradé en 2023 par rapport à 2022, et quel était ce taux ?"*
- **Traitement :** Action parallèle. 
  1. Le moteur SQL récupère la série temporelle du taux HTG/USD pour 22-23.
  2. Le moteur RAG cherche les explications de la dépréciation dans les rapports 2023.
  3. L'Interface (ou un LLM de synthèse final) combine : Le graphique + le paragraphe explicatif sourcé.

---

## 3. Stratégie Anti-Hallucination & Fiabilité B2B

Dans l'intelligence économique institutionnelle, *une absence de réponse vaut 1000 fois mieux qu'une fausse réponse.*

### 3.1 Prompting Défensif (Strict Grounding)
Le "System Prompt" du LLM générateur chargé du RAG doit intégrer des directives impérieuses :
*   `"Tu es un analyste économique expert d'Haïti. Tu dois répondre STRICTEMENT et UNIQUEMENT à partir du contexte fourni ci-dessous."`
*   `"Si la réponse à la question de l'utilisateur ne se trouve pas dans le contexte fourni, tu DOIS répondre : 'Je ne dispose pas de documents officiels permettant de réponde à cette question de manière sourcée', même si tu penses connaître la réponse grâce à ton apprentissage général."`
*   `"Tu n'es pas autorisé à déduire ou inventer des données statistiques qui ne sont pas explicitement écrites."`

### 3.2 Vérification croisée (Cross-Check LLM) - Optionnel pour V2
Pour les requêtes à fort enjeu, utiliser un second LLM (plus petit et rapide) comme "Juge" : il prend la réponse générée et le contexte RAG initial, et vérifie si la réponse déborde du contexte. Si oui, la réponse est censurée.

---

## 4. Gestion des Citations (Lineage Transparency)

### 4.1 Granularité de la Citation
L'objectif est que chaque affirmation de l'IA soit traçable. 
- **Règle :** Chaque paragraphe (voire chaque phrase métier importante) de la sortie RAG doit se terminer par un marqueur de source `[Source n]`.
- En UI, ce marqueur devient un bouton ou un encart cliquable.

### 4.2 Métadonnées requises
Le découpage des PDF ("Chunking") doit impérativement attacher à chaque paragraphe (Chunk) un objet JSON contenant :
```json
{
  "doc_title": "Note sur la Politique Monétaire",
  "institution": "BRH",
  "date_pub": "2023-11",
  "page_number": 14,
  "chunk_text": "L'inflation s'explique par...",
  "pdf_url": "https://storage.hdi.com/brh_q3_2023.pdf#page=14"
}
```
*Le LLM utilisera ces métadonnées pour rédiger la citation exacte.*

---

## 5. Gestion des Données Contradictoires

### 5.1 En données structurées
*Voir la stratégie de Résolution (strategie_sources.md).*
- Privilégier les sources internationales (Banque Mondiale) pour les comparaisons.
- Le Dashboard doit toujours afficher le logo ou le nom de la source au-dessus d'un graphique (ex: *"Source: IHSI"*).
- En cas de double source pour un même indicateur dans l'API, forcer l'utilisateur à choisir via un filtre ou définir la Banque Mondiale par défaut.

### 5.2 Dans le RAG (Conflits textuels)
*Scénario : Le document A indique une perspective positive, le document B une perspective négative.*
- **L'IA ne doit pas prendre parti ni faire de moyenne d'opinions.**
- **Règle de prompt :** Le LLM doit utiliser une structure comparative explicite s'il détecte des sources divergentes. 
- **Exemple de rendu attendu :** *"Les perspectives divergent selon les institutions. D'un côté, le FMI (Art. IV, 2023) souligne une stabilisation conjoncturelle [1]. Cependant, les notes de la BRH de la même période insistent sur le maintien de pressions récessionnistes [2]."*
- **Pondération temporelle :** Lors de la recherche sémantique (Vector Search), l'algorithme est configuré pour appliquer un "Boost" aux documents récents. Un rapport de Q3-2023 écrasera sémantiquement un rapport de Q1-2023 si la question concerne l'actualité.
