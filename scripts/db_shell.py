import sys
import os
import pandas as pd
from sqlalchemy import create_engine, text

# Ajouter le répertoire racine au path
sys.path.append(os.getcwd())

from backend.core.config import settings

def run_query(query: str):
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            if df.empty:
                print("\nℹ Aucun résultat trouvé.")
            else:
                print("\n" + df.to_markdown(index=False))
    except Exception as e:
        print(f"\n❌ Erreur SQL : {e}")

def main():
    print("=== HDI DATABASE TERMINAL TESTER ===")
    print(f"Base chargée : {settings.DATABASE_URL}")
    print("\nOptions rapides :")
    print("1. Liste des pays : 'SELECT * FROM pays'")
    print("2. Derniers indicateurs : 'SELECT * FROM vue_derniers_indicateurs LIMIT 10'")
    print("3. Statistiques par source : 'SELECT count(*) as total, dataset_id FROM valeurs_indicateurs GROUP BY dataset_id'")
    
    while True:
        try:
            query = input("\nEntrez votre requête SQL (ou 'exit' pour quitter) : ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
            run_query(query)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
