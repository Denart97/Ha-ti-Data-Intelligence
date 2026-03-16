import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.getcwd())

from backend.db.pg_session import SessionLocal
from backend.models.sql_models import ValeurIndicateur, Pays, Indicateur
from sqlalchemy import func

def final_count():
    db = SessionLocal()
    try:
        # Groupement par source (stockée dans metadata_json)
        # Note: metadata_json est un type JSON, on y accède différemment selon la DB
        # Pour SQLite, on utilise ->> ou json_extract
        
        # On va simplement boucler et compter pour être sûr
        all_vals = db.query(ValeurIndicateur).all()
        counts = {}
        for v in all_vals:
            source = v.metadata_json.get("source", "Inconnue")
            counts[source] = counts.get(source, 0) + 1
            
        print("| Source | Statut | Points de données | Observations |")
        print("| :--- | :--- | :--- | :--- |")
        for source, count in counts.items():
            status = "✅ Succès" if count > 0 else "❌ Échec"
            obs = "Données historiques chargées" if source != "BRH" else "Taux de change temps réel"
            print(f"| {source} | {status} | {count} | {obs} |")
            
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    final_count()
