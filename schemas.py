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
    phase1_empatizar: Optional[Dict[str, Any]] = None
    phase2_definir: Optional[Dict[str, Any]] = None
    phase3_idear: Optional[Dict[str, Any]] = None
    phase4_prototipar: Optional[Dict[str, Any]] = None
    phase5_testear: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    id: int
    owner_id: int
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
    full_name: str
    age: int
    school: str
    grade: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    school: str | None = None
    grade: str | None = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True