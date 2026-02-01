# main.py
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

import models
import schemas
from database import SessionLocal, engine

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

# --- INICIALIZACIÓN ---
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
static_path = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory="templates")

# --- SEGURIDAD ---
import os
SECRET_KEY = os.getenv("SECRET_KEY", "clave_temporal_solo_desarrollo")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

models.Base.metadata.create_all(bind=engine)

# --- DEPENDENCIAS Y UTILIDADES ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError: raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None: raise credentials_exception
    return user

# --- RUTAS DE API ---

@app.get("/")
def read_root():
    return {"mensaje": "API b.e Operativa"}

@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el usuario ya existe
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    # 2. Crear la instancia del modelo con los NUEVOS campos
    new_user = models.User(
        username=user.username,
        password=get_password_hash(user.password),
        full_name=user.full_name,
        birth_date=user.birth_date,
        school=user.school, 
        grade=user.grade     
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrecto")
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer"}

@app.put("/users/me/profile")
def update_user_profile(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.birth_date is not None:          
        current_user.birth_date = user_update.birth_date  
    if user_update.school is not None:
        current_user.school = user_update.school
    if user_update.grade is not None:
        current_user.grade = user_update.grade
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Perfil actualizado correctamente", "user": current_user.username}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# PROYECTOS
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_project = models.Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=list[schemas.Project])
def read_my_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    db.delete(db_project)
    db.commit()
    return None

# --- VISTAS FRONTEND ---
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request): return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/project/view/{project_id}", response_class=HTMLResponse)
def project_workspace_page(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    return templates.TemplateResponse("project_view.html", {"request": request, "project": project, "project_id": project_id})

@app.get("/project/summary/{project_id}", response_class=HTMLResponse)
def project_summary(project_id: int, request: Request, db: Session = Depends(get_db)):

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    return templates.TemplateResponse("summary.html", {
        "request": request, 
        "project": project
    })