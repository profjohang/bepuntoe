# schemas.py
from pydantic import BaseModel
from typing import Optional, List

# --- MOLDES PARA PROYECTOS ---
# Esto valida los datos cuando creamos o leemos un proyecto
class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phase1_empatizar: Optional[str] = None
    phase2_definir: Optional[str] = None
    phase3_idear: Optional[str] = None
    phase4_prototipar: Optional[str] = None
    phase5_testear: Optional[str] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    # Las fases son opcionales al inicio (pueden estar vacías)
    phase1_empatizar: Optional[str] = ""
    phase2_definir: Optional[str] = ""
    phase3_idear: Optional[str] = ""
    phase4_prototipar: Optional[str] = ""
    phase5_testear: Optional[str] = ""

    class Config:
        from_attributes = True

# --- MOLDES PARA USUARIOS ---
# Esto valida los datos del usuario
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    projects: List[Project] = []

    class Config:
        from_attributes = True