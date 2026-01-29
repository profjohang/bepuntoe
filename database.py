# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Tu URL con el puerto 3307 que configuramos
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3307/b_e_database"

# 2. Motor de conexión revisado

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# 3. Sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase Base
Base = declarative_base()