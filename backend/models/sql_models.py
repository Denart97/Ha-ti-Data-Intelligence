from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, JSON, CheckConstraint, UniqueConstraint, Uuid
from sqlalchemy.sql import func
import uuid
from backend.db.pg_session import Base

class Pays(Base):
    __tablename__ = "pays"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    iso_alpha3 = Column(String(3), unique=True, nullable=False)
    nom_fr = Column(String(100), nullable=False)
    nom_en = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Source(Base):
    __tablename__ = "sources"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    nom = Column(String(100), unique=True, nullable=False)
    type_institution = Column(String(50))
    fiabilite_score = Column(Integer)
    site_web = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('fiabilite_score >= 0 AND fiabilite_score <= 10', name='check_fiabilite'),
    )

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id = Column(Uuid, ForeignKey("sources.id", ondelete="CASCADE"))
    code_dataset = Column(String(100), nullable=False)
    url_origine = Column(String)
    frequence_maj = Column(String(20))
    last_updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Indicateur(Base):
    __tablename__ = "indicateurs"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    code_indicateur = Column(String(50), unique=True, nullable=False)
    nom = Column(String(255), nullable=False)
    description = Column(String)
    unite_mesure = Column(String(50))
    grand_domaine = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ValeurIndicateur(Base):
    __tablename__ = "valeurs_indicateurs"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    indicateur_id = Column(Uuid, ForeignKey("indicateurs.id", ondelete="CASCADE"))
    pays_id = Column(Uuid, ForeignKey("pays.id", ondelete="CASCADE"))
    dataset_id = Column(Uuid, ForeignKey("datasets.id"))
    date_valeur = Column(Date, nullable=False)
    valeur_numerique = Column(Float)
    statut = Column(String(20), default="FINAL")
    date_ingestion = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON) # Nommé metadata_json pour éviter conflit avec SQLAlchemy metadata

    __table_args__ = (
        UniqueConstraint('indicateur_id', 'pays_id', 'date_valeur', 'statut', name='unique_valeur'),
    )
