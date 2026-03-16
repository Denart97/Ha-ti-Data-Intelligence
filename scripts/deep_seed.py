import sys
import os
import uuid
from datetime import date
from sqlalchemy.dialects.sqlite import insert

# Ajouter le répertoire racine au path
sys.path.append(os.getcwd())

from backend.db.pg_session import SessionLocal, engine, Base
from backend.models.sql_models import Pays, Source, Indicateur, Dataset, ValeurIndicateur
# On assume que les modèles Document et Chunk ont été ajoutés selon l'architecture
from sqlalchemy import Column, String, Integer, Date, ForeignKey, JSON, Uuid, text

# Définition locale des modèles si non présents dans sql_models.py (pour compatibilité)
class Document(Base):
    __tablename__ = "documents"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id = Column(Uuid, ForeignKey("sources.id"))
    titre = Column(String(255), nullable=False)
    date_publication = Column(Date)
    url_pdf = Column(String)
    content_hash = Column(String(64), unique=True)
    metadata_json = Column(JSON)

class Chunk(Base):
    __tablename__ = "chunks_documentaires"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id = Column(Uuid, ForeignKey("documents.id"))
    vector_id = Column(String(100), unique=True)
    page_numero = Column(Integer)
    texte_contenu = Column(String, nullable=False)

def deep_seed():
    print("--- DEEP SEEDING (SQL + DOCUMENTARY) ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Récupération des IDs de base
        brh_id = db.query(Source.id).filter_by(nom="BRH").scalar()
        fmi_id = db.query(Source.id).filter_by(nom="FMI").scalar()
        hti_id = db.query(Pays.id).filter_by(iso_alpha3="HTI").scalar()

        # 2. Ajout de Documents "Seed"
        doc_brh = Document(
            id=uuid.uuid4(),
            source_id=brh_id,
            titre="Note sur la Politique Monétaire - Octobre 2023",
            date_publication=date(2023, 10, 15),
            content_hash="fake_hash_brh_001",
            metadata_json={"official_id": "BRH-2023-Q4"}
        )
        db.merge(doc_brh)
        
        # 3. Ajout de Chunks "Seed" (Contenu textuel pour le RAG)
        chunk_1 = Chunk(
            id=uuid.uuid4(),
            document_id=doc_brh.id,
            vector_id="vec_brh_001",
            page_numero=1,
            texte_contenu="L'inflation en Haïti a atteint 22.5% en glissement annuel au mois de septembre 2023, tirée principalement par les prix des produits alimentaires importés."
        )
        chunk_2 = Chunk(
            id=uuid.uuid4(),
            document_id=doc_brh.id,
            vector_id="vec_brh_002",
            page_numero=3,
            texte_contenu="Le taux de change de référence de la BRH s'est stabilisé autour de 132 gourdes pour un dollar américain, grâce aux interventions sur le marché des changes."
        )
        db.merge(chunk_1)
        db.merge(chunk_2)

        db.commit()
        print("✔ Documents et Chunks 'Seed' insérés en base relationnelle.")
        
        # 4. Activation manuelle de ChromaDB pour ces documents
        from backend.db.vector_store import vector_store
        collection = vector_store.get_collection()
        
        # On injecte les mêmes textes dans ChromaDB pour que le RAG les trouve
        collection.add(
            ids=["vec_brh_001", "vec_brh_002"],
            documents=[chunk_1.texte_contenu, chunk_2.texte_contenu],
            metadatas=[
                {"source": "BRH", "filename": doc_brh.titre, "page": 1, "db_chunk_id": str(chunk_1.id)},
                {"source": "BRH", "filename": doc_brh.titre, "page": 3, "db_chunk_id": str(chunk_2.id)}
            ]
        )
        print("✔ Chunks indexés dans ChromaDB (Vector Store).")

        print("\n--- SYSTÈME INITIALISÉ POUR TESTS HYBRIDES ---")
        
    except Exception as e:
        print(f"❌ Erreur Deep Seed : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    deep_seed()
