import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.getcwd())

from backend.db.vector_store import vector_store

def diagnostic_chroma():
    print("--- DIAGNOSTIC CHROMADB ---")
    try:
        n_chunks = vector_store.get_items_count()
        collection = vector_store.get_collection()
        results = collection.get(limit=100)
        
        filenames = set()
        if results and "metadatas" in results:
            for meta in results["metadatas"]:
                if meta and "filename" in meta:
                    filenames.add(meta["filename"])
        
        print(f"\n[ChromaDB]")
        print(f"- Documents ingérés : {len(filenames)}")
        print(f"- Chunks indexés : {n_chunks}")
        if filenames:
            print(f"- Fichiers présents : {list(filenames)}")
        else:
            print("- Aucun document identifié par métadonnées.")
            
    except Exception as e:
        print(f"\n[Erreur ChromaDB] : {e}")

if __name__ == "__main__":
    diagnostic_chroma()
