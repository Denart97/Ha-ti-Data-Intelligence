from backend.db.pg_session import SessionLocal
from backend.models.sql_models import ValeurIndicateur, Indicateur, Pays, Source, Dataset
import datetime

def seed():
    db = SessionLocal()
    try:
        # Récupération des entités de base
        ind = db.query(Indicateur).filter(Indicateur.code_indicateur == 'USD_HTG_REF').first()
        hti = db.query(Pays).filter(Pays.iso_alpha3 == 'HTI').first()
        src = db.query(Source).filter(Source.nom == 'BRH').first()
        
        if not all([ind, hti, src]):
            print(f"Missing entities: Ind={ind}, Pays={hti}, Source={src}")
            return

        # Récupération ou création d'un Dataset pour BRH
        ds = db.query(Dataset).filter(Dataset.source_id == src.id).first()
        if not ds:
            ds = Dataset(source_id=src.id, code_dataset="BRH_EXCHANGE", url_origine="https://www.brh.ht")
            db.add(ds)
            db.flush()

        # Ajout de 24 mois de données fictives basées sur une tendance stable (132 HTG/USD)
        for i in range(24):
            date_val = datetime.date.today() - datetime.timedelta(days=30*i)
            val = 132.5 + (i * 0.1) # Légère variation
            
            # Vérifier si le point existe déjà
            existing = db.query(ValeurIndicateur).filter(
                ValeurIndicateur.indicateur_id == ind.id,
                ValeurIndicateur.date_valeur == date_val
            ).first()
            
            if not existing:
                dp = ValeurIndicateur(
                    indicateur_id=ind.id,
                    pays_id=hti.id,
                    dataset_id=ds.id,
                    valeur_numerique=val,
                    date_valeur=date_val,
                    statut='FINAL'
                )
                db.add(dp)
        
        db.commit()
        print("Successfully seeded USD_HTG_REF data.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
