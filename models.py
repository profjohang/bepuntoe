# models.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Tabla de Usuarios
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    
    projects = relationship("Project", back_populates="owner")

# Tabla de Proyectos
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    
    # CAMBIO IMPORTANTE: Usamos JSON en lugar de Text
    # default={} asegura que empiece como un objeto vacío y no como null
    phase1_empatizar = Column(JSON, default={}) 
    phase2_definir = Column(JSON, default={})
    phase3_idear = Column(JSON, default={})
    phase4_prototipar = Column(JSON, default={})
    phase5_testear = Column(JSON, default={})

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")

    