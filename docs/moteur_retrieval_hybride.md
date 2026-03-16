# Moteur de Retrieval Hybride : Haiti Data Intelligence

Ce document détaille l'architecture du "Cerveau" de la plateforme : le moteur capable d'orchestrer les requêtes entre la base de données relationnelle (SQL) et la base vectorielle (RAG).

---

## 1. Logique de Classification & Routage (The Router)

Le point d'entrée unique analyse la requête utilisateur pour déterminer le pipeline optimal.

| Intent | Description | Pipeline |
| :--- | :--- | :--- |
| **DATA_QUANT** | Questions sur des chiffres exacts, tendances, comparaisons. | `Text-to-SQL` |
| **DOC_QUALIT** | Questions sur des analyses, rapports, contexte politique. | `Vector RAG` |
| **HYBRID** | Questions nécessitant un chiffre ET son explication. | `Parallel Execution` |
| **META** | Questions sur le catalogue ou les sources. | `SQL Registry` |

### 1.1 Processus de classification
Un LLM léger (ex: GPT-4o-mini ou Claude Haiku) est utilisé avec un prompt de classification systémique :
1. **Extraction des entités :** Pays, Indicateur, Période.
2. **Détection du besoin :** "Est-ce que je cherche une valeur (`NUMERIC`) ou une explication (`TEXT`) ?"
3. **Sortie JSON :** `{"intent": "HYBRID", "entities": {...}, "reasoning": "..."}`

---

## 2. Logique de Retrieval (Accès aux Connaissances)

### 2.1 Branche A : Le moteur SQL (Structured)
1. **Génération de Query :** Passage du langage naturel au SQL PostgreSQL via un schéma "Read-Only".
2. **Exécution :** Récupération des séries temporelles (ex: Inflation HTI 2010-2023).
3. **Formatage :** Conversion du ResultSet en tableau Markdown ou synthèse statistique compacte.

### 2.2 Branche B : Le moteur Vectoriel (Unstructured)
1. **Embedding :** Vectorisation de la requête utilisateur.
2. **Similarity Search :** Récupération des Top-K chunks (ex: 10 chunks) dans ChromaDB.
3. **Pre-filtering :** Application des filtres durs (Date, Source) basés sur les entités extraites.

---

## 3. Reranking & Fusion

### 3.1 Reranking (RAG)
Pour améliorer la précision, un modèle de **Cross-Encoder** (Reranker) ré-évalue les 10 chunks pour n'en garder que les 4-5 les plus pertinents par rapport à la question.

### 3.2 Fusion des résultats
Les résultats SQL (tables) et RAG (textes) sont fusionnés dans un "Context Bundle" :
```text
CONTEXT_DATA: [Tableau PIB Haïti 2022: 14.5Mrd USD]
CONTEXT_DOCS: ["Le rapport de la BRH souligne que la croissance est freinée par l'instabilité..."]
```

---

## 4. Logique de Réponse Finale & Citations

Le LLM de synthèse génère la réponse finale en respectant les consignes :
1. **Grounding strict :** Interdiction de citer des chiffres non présents dans `CONTEXT_DATA`.
2. **Style :** Neutre, professionnel, analytique.
3. **Citations :** Chaque affirmation tirée d'un document doit porter un index `[1]`, `[2]` renvoyant vers la table `citations` du schéma.

---

## 5. Pseudo-code du Moteur (Pythonic)

```python
async def hybrid_query_engine(user_query: str):
    # 1. Classification de l'intention
    intent_data = await llm_router.classify(user_query)
    
    tasks = []
    
    # 2. Lancement des recherches en parallèle
    if intent_data.intent in ["DATA_QUANT", "HYBRID"]:
        tasks.append(sql_engine.execute_query(user_query, intent_data.entities))
        
    if intent_data.intent in ["DOC_QUALIT", "HYBRID"]:
        tasks.append(vector_engine.retrieve(user_query, top_k=10))
        
    results = await asyncio.gather(*tasks)
    
    # 3. Traitement des résultats
    sql_ctx = results[0] if intent_data.intent == "HYBRID" or intent_data.intent == "DATA_QUANT" else None
    rag_raw = results[1] if intent_data.intent == "HYBRID" else (results[0] if intent_data.intent == "DOC_QUALIT" else None)
    
    # 4. Reranking des documents si nécessaire
    rag_ctx = reranker.process(user_query, rag_raw) if rag_raw else []
    
    # 5. Synthèse finale
    final_response = await llm_synthesizer.generate(
        query=user_query,
        data_context=sql_ctx,
        doc_context=rag_ctx
    )
    
    return {
        "answer": final_response.text,
        "sources": final_response.citations,
        "data_table": sql_ctx.as_markdown() if sql_ctx else None,
        "intent": intent_data.intent
    }
```

---

## 6. Recommandations de Performance

*   **Caching :** Mettre en cache les résultats SQL pour les indicateurs très demandés (ex: Taux de change du jour).
*   **Latency :** Utiliser des appels asynchrones (`asyncio`) pour ne pas attendre que le SQL finisse avant de lancer la recherche vectorielle.
*   **Hallucination Check :** Un "Validator" LLM peut repasser sur la réponse finale pour vérifier que les chiffres cités correspondent exactement au `sql_ctx`.
