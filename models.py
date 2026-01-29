from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para manejar fechas automáticas
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # Perfil del estudiante (Nuevos campos con límites)
    full_name = Column(String(150))
    age = Column(Integer)
    school = Column(String(150))
    grade = Column(String(50))
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación: Si se borra el usuario, se borran sus proyectos (cascade)
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), index=True, nullable=False)
    description = Column(String(500))
    
    # Fases del Design Thinking (JSON)
    # Es recomendable inicializarlos como diccionarios vacíos en el esquema más adelante
    phase1_empathize = Column(JSON)
    phase2_define = Column(JSON)
    phase3_ideate = Column(JSON)
    phase4_prototype = Column(JSON)
    phase5_test = Column(JSON)

    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
