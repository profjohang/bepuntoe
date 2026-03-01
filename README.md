# b.e 🚀

**Plataforma de gestión de proyectos con enfoque en Design Thinking.**

Este proyecto es un MVP desarrollado con **FastAPI** que permite a los usuarios registrarse y gestionar sus emprendimientos sociales siguiendo las fases de Empatizar, Definir, Idear, Prototipar y Testear.

## ✨ Características Principales

* **Autenticación Segura:** Registro e inicio de sesión utilizando **JWT (JSON Web Tokens)** y encriptación de contraseñas con **bcrypt**.
* **Gestión de Proyectos:** Creación, edición y visualización de emprendimientos vinculados a cada usuario.
* **Enfoque Pedagógico:** Estructurado para guiar el proceso de diseño centrado en el usuario.
* **Perfil de Usuario Extendido:** Almacena información sobre el colegio, grado y fecha de nacimiento.

## 🛠️ Tecnologías Utilizadas

* **Backend:** FastAPI
* **Base de Datos:** SQLite / MySQL con **SQLAlchemy** como ORM
* **Seguridad:** Passlib (bcrypt) y Python-Jose (JWT)
* **Frontend:** Jinja2 Templates, HTML5 y CSS3

## 🚀 Instalación y Configuración

1. **Clonar el repositorio.**
2. **Crear y activar entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

```


3. **Instalar dependencias:**
```bash
pip install -r requirements.txt

```


4. **Configurar variables de entorno:**
Crea un archivo `.env` en la raíz con:
```env
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3307/b_e_database

```


5. **Ejecutar la aplicación:**
```bash
uvicorn main:app --reload

```



## 📂 Estructura del Proyecto

* `main.py`: Punto de entrada, rutas de la API y lógica de autenticación.
* `models.py`: Modelos de la base de datos (Usuarios y Proyectos).
* `schemas.py`: Esquemas de validación de datos con Pydantic.
* `database.py`: Configuración de la conexión a la base de datos.
* `templates/`: Plantillas HTML para la interfaz de usuario.
