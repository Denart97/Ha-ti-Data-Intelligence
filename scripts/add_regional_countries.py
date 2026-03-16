from backend.db.pg_session import SessionLocal
from backend.models.sql_models import Pays

def add_countries():
    db = SessionLocal()
    try:
        new_countries = [
            {"iso_alpha3": "CUB", "nom_fr": "Cuba", "nom_en": "Cuba"},
            {"iso_alpha3": "JAM", "nom_fr": "Jamaïque", "nom_en": "Jamaica"}
        ]
        
        for c_data in new_countries:
            exists = db.query(Pays).filter(Pays.iso_alpha3 == c_data["iso_alpha3"]).first()
            if not exists:
                country = Pays(**c_data)
                db.add(country)
                print(f"Added: {c_data['nom_fr']}")
            else:
                print(f"Already exists: {c_data['nom_fr']}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_countries()
