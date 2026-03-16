import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.getcwd())

from backend.db.pg_session import SessionLocal
from backend.models.sql_models import Pays, Indicateur, ValeurIndicateur, Source, Dataset
from backend.db.vector_store import vector_store
from sqlalchemy import func

def diagnostic():
    print("--- DIAGNOSTIC TECHNIQUE DES DONNÉES ---")
    
    # 1. Diagnostic PostgreSQL
    db = SessionLocal()
    try:
        n_pays = db.query(func.count(Pays.id)).scalar()
        n_indicators = db.query(func.count(Indicateur.id)).scalar()
        n_values = db.query(func.count(ValeurIndicateur.id)).scalar()
        n_sources = db.query(func.count(Source.id)).scalar()
        n_datasets = db.query(func.count(Dataset.id)).scalar()
        
        print(f"\n[PostgreSQL]")
        print(f"- Pays chargés : {n_pays}")
        print(f"- Indicateurs définis : {n_indicators}")
        print(f"- Valeurs stockées : {n_values}")
        print(f"- Sources référencées : {n_sources}")
        print(f"- Datasets actifs : {n_datasets}")
        
        if n_pays > 0:
            pays_list = db.query(Pays.iso_alpha3).all()
            print(f"- ISO Pays : {[p[0] for p in pays_list]}")
            
        if n_sources > 0:
            sources_list = db.query(Source.nom).all()
            print(f"- Sources : {[s[0] for s in sources_list]}")
            
    except Exception as e:
        print(f"\n[Erreur PostgreSQL] : {e}")
    finally:
        db.close()
        
    # 2. Diagnostic ChromaDB
    try:
        n_chunks = vector_store.get_items_count()
        collection = vector_store.get_collection()
        results = collection.get(limit=100)
        
        # Extraire les documents uniques (généralement via metadata 'filename')
        filenames = set()
        if results and "metadatas" in results:
            for meta in results["metadatas"]:
                if meta and "filename" in meta:
                    filenames.add(meta["filename"])
        
        print(f"\n[ChromaDB]")
        print(f"- Documents ingérés (estimés) : {len(filenames)}")
        print(f"- Chunks indexés : {n_chunks}")
        if filenames:
            print(f"- Fichiers présents : {list(filenames)}")
            
    except Exception as e:
        print(f"\n[Erreur ChromaDB] : {e}")

if __name__ == "__main__":
    diagnostic()
