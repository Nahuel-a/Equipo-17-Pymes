# 📋 Plataforma Web de Onboarding de Créditos para PYMES

Plataforma web FinTech que permite a las PYMES solicitar créditos de manera digital, cargar documentos y realizar firmas digitales en un proceso completamente online.

---

## 🚀 Tecnologías

### Backend

* **Python 3.11+** – Lenguaje principal
* **FastAPI** – Framework web moderno y rápido
* **PostgreSQL** – Base de datos relacional
* **SQLAlchemy** – ORM para gestión de base de datos
* **Alembic** – Migraciones de base de datos
* **JWT** – Autenticación segura
* **Pydantic** – Validación de datos

### Frontend

* **Vanilla JavaScript** – Sin frameworks pesados
* **HTML5** – Estructura semántica
* **CSS3 + Bootstrap 5** – Estilos responsivos
* **Fetch API** – Cliente HTTP nativo para APIs

---

## 🏗️ Arquitectura

### Backend (MVC)

```
back/app/
├── controllers/     # Lógica de negocio
├── models/          # Modelos de datos SQLAlchemy  
├── views/           # Schemas Pydantic
├── services/        # Lógica reutilizable
├── routers/         # Endpoints FastAPI
└── core/            # Configuración y base de datos
```

### Frontend

```
front/src/
├── models/          # Modelos de datos
├── views/           # Componentes UI
├── controllers/     # Controladores de lógica
└── styles/          # CSS y Bootstrap
```

---

## 🛠️ Configuración del Entorno de Desarrollo

### 🔹 Opción 1: Instalación Tradicional (Sin Docker)

#### Windows

```bash
# Instalar PostgreSQL
download: postgresql.org/download/windows/

# Crear base de datos
createdb -U postgres credit_db

# Backend
cd back
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Variables de entorno
set DATABASE_URL=postgresql://postgres:password@localhost:5432/credit_db
set SECRET_KEY=tu-clave-secreta-aqui

# Migraciones y servidor
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Linux / macOS

```bash
# Instalar PostgreSQL
sudo apt update && sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres createdb credit_db
sudo -u postgres createuser -P credit_user

# Backend
cd back
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Variables de entorno
export DATABASE_URL=postgresql://credit_user:password@localhost:5432/credit_db
export SECRET_KEY=tu-clave-secreta-aqui

# Migraciones y servidor
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend (todos los sistemas)

```bash
cd front
npm install
npm run dev
```

### 🔹 Opción 2: Docker (Recomendado)

```bash
# Ejecutar todo con un solo comando
docker-compose up -d

# URLs de acceso:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5432
```

---

## 🐳 Docker - Vista Previa para Despliegue

### Estructura básica `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: credit_db
      POSTGRES_USER: credit_user
      POSTGRES_PASSWORD: credit_pass
    ports: ["5432:5432"]

  backend:
    build: ./back
    ports: ["8000:8000"]
    depends_on: [postgres]

  frontend:
    build: ./front  
    ports: ["3000:3000"]
    depends_on: [backend]
```

### Ventajas de usar Docker

* ✅ Entorno consistente entre desarrollo y producción
* ✅ Configuración rápida con un solo comando
* ✅ Aislamiento de dependencias
* ✅ Facilita el despliegue en cualquier infraestructura

---

## 🔀 Git Flow Profesional Simplificado

### Ramas principales

* **main** → Producción (solo releases estables)
* **develop** → Desarrollo (integración continua)
* **feature/*** → Nuevas funcionalidades
* **bugfix/*** → Corrección de bugs
* **hotfix/*** → Correcciones urgentes

### Convención de nombrado

```
{type}/{descripcion-corta}
```

Ejemplos:

* `feature/autenticacion-jwt`
* `bugfix/validacion-email`
* `hotfix/login-timeout`
* `release/v1.2.0`

### Flujo de trabajo

```bash
# 1. Crear rama desde develop
git checkout develop && git pull
git checkout -b feature/nueva-funcionalidad

# 2. Desarrollar con commits semánticos
git add .
git commit -m "feat: implementar nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# 3. Crear Pull Request a develop
# 4. Después del merge, limpiar rama
```

---

## 🚀 Comandos de Desarrollo

### Backend

```bash
# Desarrollo tradicional
uvicorn app.main:app --reload --port 8000

# Con Docker
docker-compose up backend -d

# Migraciones
alembic upgrade head
```

### Frontend

```bash
# Desarrollo tradicional
npm run dev

# Con Docker
docker-compose up frontend -d
```

---

## 📊 Comparación: Desarrollo Tradicional vs Docker

| Aspecto       | Tradicional                   | Docker                     |
| ------------- | ----------------------------- | -------------------------- |
| Configuración | Manual por cada desarrollador | Automática y consistente   |
| Tiempo setup  | 15-30 minutos                 | 2-5 minutos                |
| Dependencias  | Instaladas localmente         | Aisladas en contenedores   |
| Base de datos | Instalación local separada    | Incluida en el stack       |
| Portabilidad  | Depende del SO                | Igual en cualquier sistema |

---

## 🎯 Próximos Pasos

### Para desarrollo inmediato

* Usar instalación tradicional para inicio rápido
* Seguir la arquitectura **MVC** establecida
* Implementar **Git Flow** desde el inicio

### Para preparar producción

* Implementar **Docker** en el repositorio
* Configurar variables de entorno para diferentes ambientes
* Preparar scripts de despliegue

👉 Recomendación: comenzar con instalación tradicional y migrar a Docker cuando el proyecto esté más estable, para facilitar despliegue y consistencia de ambientes.
