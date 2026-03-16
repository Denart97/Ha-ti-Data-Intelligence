import sys
import os
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import text

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.getcwd())

from backend.db.pg_session import SessionLocal, engine, Base
from backend.models.sql_models import Pays, Source, Indicateur, Dataset

def seed():
    print("--- INITIALISATION ET SEEDING SQLITE ---")
    
    # Création des tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    print("✔ Tables créées ou vérifiées.")

    db = SessionLocal()
    try:
        # 1. Pays
        pays_data = [
            {"iso_alpha3": "HTI", "nom_fr": "Haïti", "nom_en": "Haiti"},
            {"iso_alpha3": "DOM", "nom_fr": "République Dominicaine", "nom_en": "Dominican Republic"}
        ]
        for p in pays_data:
            stmt = insert(Pays).values(**p).on_conflict_do_nothing()
            db.execute(stmt)
        print("✔ Pays peuplés.")

        # 2. Sources
        sources_data = [
            {"nom": "Banque Mondiale", "type_institution": "Internationale", "fiabilite_score": 9},
            {"nom": "FMI", "type_institution": "Internationale", "fiabilite_score": 9},
            {"nom": "BRH", "type_institution": "Nationale", "fiabilite_score": 8},
            {"nom": "IHSI", "type_institution": "Nationale", "fiabilite_score": 7}
        ]
        for s in sources_data:
            stmt = insert(Source).values(**s).on_conflict_do_nothing()
            db.execute(stmt)
        print("✔ Sources peuplées.")

        # 3. Indicateurs
        indicators_data = [
            {"code_indicateur": "GDP", "nom": "PIB (Croissance annuelle %)", "unite_mesure": "%", "grand_domaine": "MACRO"},
            {"code_indicateur": "INFLATION", "nom": "Inflation (Prix à la consommation %)", "unite_mesure": "%", "grand_domaine": "MACRO"},
            {"code_indicateur": "USD_HTG_REF", "nom": "Taux de change de référence (USD/HTG)", "unite_mesure": "HTG", "grand_domaine": "MONETAIRE"},
            {"code_indicateur": "UNEMPLOYMENT", "nom": "Taux de chômage (% population active)", "unite_mesure": "%", "grand_domaine": "SOCIAL"},
            {"code_indicateur": "FDI", "nom": "Investissements directs étrangers (% PIB)", "unite_mesure": "%", "grand_domaine": "ECONOMIE"},
            {"code_indicateur": "EDUCATION_EXP", "nom": "Dépenses publiques en éducation (% PIB)", "unite_mesure": "%", "grand_domaine": "SOCIAL"},
            {"code_indicateur": "HEALTH_EXP", "nom": "Dépenses publiques en santé (% PIB)", "unite_mesure": "%", "grand_domaine": "SOCIAL"}
        ]
        for i in indicators_data:
            stmt = insert(Indicateur).values(**i).on_conflict_do_nothing()
            db.execute(stmt)
        print("✔ Indicateurs peuplés.")
        
        # 4. Datasets
        db.commit() 
        wb_id = db.query(Source.id).filter_by(nom="Banque Mondiale").scalar()
        imf_id = db.query(Source.id).filter_by(nom="FMI").scalar()
        
        datasets_data = [
            {"source_id": wb_id, "code_dataset": "WDI", "frequence_maj": "ANNUEL"},
            {"source_id": imf_id, "code_dataset": "IFS", "frequence_maj": "MENSUEL"}
        ]
        for d in datasets_data:
            stmt = insert(Dataset).values(**d).on_conflict_do_nothing()
            db.execute(stmt)
        print("✔ Datasets peuplés.")

        # 5. Création de la vue (Spécifique SQLite)
        view_sql = """
        CREATE VIEW IF NOT EXISTS vue_derniers_indicateurs AS
        SELECT 
            p.iso_alpha3,
            i.code_indicateur,
            v.date_valeur,
            v.valeur_numerique,
            v.statut
        FROM valeurs_indicateurs v
        JOIN pays p ON v.pays_id = p.id
        JOIN indicateurs i ON v.indicateur_id = i.id
        WHERE v.statut = 'FINAL'
        AND v.date_valeur = (
            SELECT MAX(v2.date_valeur) 
            FROM valeurs_indicateurs v2 
            WHERE v2.indicateur_id = v.indicateur_id 
            AND v2.pays_id = v.pays_id 
            AND v2.statut = 'FINAL'
        );
        """
        db.execute(text(view_sql))
        print("✔ Vue 'vue_derniers_indicateurs' créée.")

        db.commit()
        print("\n--- SEEDING RÉUSSI ---")
    except Exception as e:
        print(f"\n❌ ERREUR SEEDING : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
