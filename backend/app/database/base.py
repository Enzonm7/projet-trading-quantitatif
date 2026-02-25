"""
Module base - Configuration de la connexion SQLAlchemy et session DB.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 1. DATABASE_URL : lire depuis os.getenv() avec une valeur par défaut
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/pairs_trading_db"   
)

# 2. engine : créer avec create_engine()
engine = create_engine(DATABASE_URL)

# 3. SessionLocal : créer avec sessionmaker(bind=engine)
SessionLocal = sessionmaker(bind=engine)

# 4. Base : créer avec declarative_base()
Base = declarative_base()

# 5. Fonction get_db()
def get_db():
    """
    Générateur de session DB pour l'injection de dépendances FastAPI.
    
    Yields:
        Session SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()