# schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime

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
    birth_date: date = Field(..., description="Fecha de nacimiento")
    school: str
    grade: str
    
    @field_validator('birth_date')
    @classmethod
    def validate_age(cls, v):
        """Validar que el usuario tenga entre 10 y 25 años"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 10:
            raise ValueError('Debes tener al menos 10 años para registrarte')
        if age > 25:
            raise ValueError('Debes tener máximo 25 años para registrarte')
        
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña debe tener mínimo 6 caracteres")

class UserUpdate(BaseModel):
    full_name: str | None = None
    birth_date: date | None = None
    school: str | None = None
    grade: str | None = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True