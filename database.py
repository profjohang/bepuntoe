# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definimos que usaremos SQLite (un archivo local) en lugar de un servidor complejo.
#    El archivo se llamará "b_e_database.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./b_e_database.db"

# 2. Motor de conexión.
#    "connect_args" es necesario solo para SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. "Sesión" (es lo que usaremos para guardar y pedir datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase "Base" será la mamá de todos nuestros modelos (tablas)
Base = declarative_base()