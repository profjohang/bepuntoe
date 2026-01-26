# main.py
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Annotated

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

# --- INICIALIZACIÓN ÚNICA ---
app = FastAPI()

# --- CONFIGURACIÓN DE RUTAS FÍSICAS (PARA EL LOGO) ---
BASE_DIR = Path(__file__).resolve().parent
static_path = BASE_DIR / "static"

# Montaje de archivos estáticos (Logo, CSS)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Configuración de plantillas HTML
templates = Jinja2Templates(directory="templates")

# --- DIAGNÓSTICO AUTOMÁTICO AL INICIAR ---
print(f"\n--- VERIFICACIÓN DE RECURSOS b.e ---")
if static_path.exists():
    logo_file = static_path / "images" / "logo.png"
    if logo_file.exists():
        print(f"✅ Logo detectado en: {logo_file}")
    else:
        print(f"❌ ERROR: No se encuentra logo.png en static/images/")
else:
    print(f"❌ ERROR: No se encuentra la carpeta 'static'")
print(f"------------------------------------\n")

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = "clave_secreta_proyecto_be_mvp" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Crea las tablas
models.Base.metadata.create_all(bind=engine)

# --- FUNCIONES DE AYUDA (UTILIDADES) ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Verifica si la contraseña escrita coincide con la encriptada
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Convierte la contraseña normal en una encriptada
def get_password_hash(password):
    return pwd_context.hash(password)

# Crea el "Carnet Digital" (Token) con tiempo de expiración
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para identificar al usuario actual basado en su token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- RUTAS (ENDPOINTS) ---

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de b.e - Sistema Listo"}

# 1. REGISTRO DE USUARIO
@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Buscar si ya existe alguien con ese nombre
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear usuario y guardar
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 2. LOGIN (Generar Token)
@app.post("/token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    # Buscar usuario
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    # Verificar si existe y si la contraseña es correcta
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generar token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. RUTA DE PRUEBA (Solo para usuarios logueados)
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user

# 4. CREAR UN PROYECTO
@app.post("/projects/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Creamos el modelo de base de datos usando los datos recibidos
    # El "owner_id" se llena automáticamente con el ID del usuario logueado
    db_project = models.Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# 5. VER MIS PROYECTOS
@app.get("/projects/", response_model=list[schemas.Project])
def read_my_projects(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Buscamos solo los proyectos donde el dueño sea el usuario actual
    projects = db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()
    return projects

# 6. VER UN PROYECTO ESPECÍFICO (Por ID)
@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_one_project(
    project_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Buscar el proyecto
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    # Validaciones de seguridad
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este proyecto")
        
    return project

# --- RUTAS VISUALES (FRONTEND) ---

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/project/summary/{project_id}", response_class=HTMLResponse)
def project_summary_page(project_id: int, request: Request):
    return templates.TemplateResponse("summary.html", {"request": request, "project_id": project_id})

# --- RUTAS (EDICIÓN DE PROYECTOS) ---

# GUARDAR CAMBIOS EN UN PROYECTO (PUT)

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    print(f"--> Intentando actualizar proyecto {project_id}") # DEBUG
    print(f"--> Datos recibidos: {project_update.model_dump(exclude_unset=True)}") # DEBUG

    # 1. Buscar el proyecto
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    # 2. Verificar existencia y permisos
    if not db_project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    # 3. Actualizar datos (Usando model_dump para Pydantic V2)
    try:
        update_data = project_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_project, key, value)

        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        print("--> ¡Actualización exitosa en BD!") # DEBUG
        return db_project
        
    except Exception as e:
        print(f"--> ERROR CRÍTICO AL GUARDAR: {e}") # DEBUG IMPORTANTE
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

# SERVIR LA PÁGINA DE TRABAJO (HTML)
@app.get("/project/view/{project_id}", response_class=HTMLResponse)
def project_workspace_page(project_id: int, request: Request, db: Session = Depends(get_db)):
    # 1. Buscamos el proyecto en la base de datos usando el ID
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    # 2. Si no existe, lanzamos error 
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # 3. ¡IMPORTANTE! Pasamos la variable 'project' a la plantilla
    return templates.TemplateResponse("project_view.html", {
        "request": request, 
        "project_id": project_id, 
        "project": project 
    })