# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Tabla de Usuarios
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # Nombre de usuario único
    password = Column(String) # Aquí guardaremos la contraseña
    
    # Relación: Un usuario puede tener muchos proyectos
    projects = relationship("Project", back_populates="owner")

# Tabla de Proyectos (Simplificada para el MVP)
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    
    # Guardamos las respuestas de cada fase como texto largo en estas columnas.
    phase1_empatizar = Column(Text, default="") 
    phase2_definir = Column(Text, default="")
    phase3_idear = Column(Text, default="")
    phase4_prototipar = Column(Text, default="")
    phase5_testear = Column(Text, default="")

    # Conexión con el usuario dueño del proyecto
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")