# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# --- MOLDES PARA PROYECTOS ---

class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    # Es vital que estas líneas existan:
    phase1_empatizar: Optional[Dict[str, Any]] = None
    phase2_definir: Optional[Dict[str, Any]] = None
    phase3_idear: Optional[Dict[str, Any]] = None
    phase4_prototipar: Optional[Dict[str, Any]] = None
    phase5_testear: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    # Definimos que la salida también será un diccionario
    phase1_empatizar: Optional[Dict[str, Any]] = {}
    phase2_definir: Optional[Dict[str, Any]] = {}
    phase3_idear: Optional[Dict[str, Any]] = {}
    phase4_prototipar: Optional[Dict[str, Any]] = {}
    phase5_testear: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True

# --- MOLDES PARA USUARIOS ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    projects: List[Project] = []

    class Config:
        from_attributes = True