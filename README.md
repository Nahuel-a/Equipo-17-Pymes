# Equipo-17-Pymes
Plataforma Web de Onboarding de Créditos para PYMES.

## Estado Actual del Proyecto

A fecha actual, el proyecto ha alcanzado un hito importante: la integración del frontend y el backend. La aplicación ahora funciona como un servicio web cohesivo donde el backend de FastAPI se encarga de servir las vistas del frontend directamente.

- **Backend (FastAPI):** Proporciona la API y la lógica de negocio.
- **Frontend (HTML/CSS/JS):** Define la interfaz de usuario.
- **Integración:** El backend sirve las páginas del frontend utilizando el motor de plantillas Jinja2, creando una única aplicación.

---

## Estructura del Proyecto

```
/
├── backend/
│   ├── app/
│   │   ├── main.py       # Archivo principal de FastAPI con las rutas
│   │   └── ...           # Resto de la lógica del backend
│   └── pyproject.toml    # Dependencias y configuración del proyecto Python
│
└── fontend/
    ├── *.html            # Plantillas de la interfaz de usuario
    ├── styles.css        # Estilos
    └── app.js            # Lógica del lado del cliente
```

---

## Cómo Ejecutar el Proyecto Localmente

Para ejecutar la aplicación en tu entorno de desarrollo, sigue estos pasos.

### Prerrequisitos

- **Python 3.12+**
- **Poetry:** Para la gestión de dependencias de Python. Si no lo tienes, sigue las [instrucciones de instalación oficiales](https://python-poetry.org/docs/#installation).

### Pasos para la Instalación

1.  **Navega al directorio del backend:**
    ```bash
    cd backend
    ```

2.  **Instala las dependencias:**
    Poetry creará un entorno virtual y descargará todo lo necesario.
    ```bash
    poetry install
    ```

3.  **Ejecuta el servidor de desarrollo:**
    Este comando inicia la aplicación con recarga automática.
    ```bash
    poetry run python -m uvicorn app.main:app --reload
    ```

4.  **Abre la aplicación:**
    Visita [`http://127.0.0.1:8000`](http://127.0.0.1:8000) en tu navegador.

---

## Siguientes Pasos

Ahora que la base de la aplicación está funcionando, los siguientes pasos se centran en implementar la funcionalidad principal y prepararla para producción.

### 1. Implementar los Endpoints de la API

Actualmente, la aplicación solo sirve las páginas (rutas GET). El siguiente paso crucial es implementar las rutas POST que recibirán los datos de los formularios de la interfaz de usuario.

- **Rutas a crear:**
    - `POST /login`: Para manejar el inicio de sesión de usuarios.
    - `POST /register`: Para registrar nuevos usuarios.
    - `POST /password-recovery`: Para gestionar la recuperación de contraseñas.
- **Lógica:** Estos endpoints deberán validar los datos de entrada, interactuar con la base de datos y devolver respuestas adecuadas (por ejemplo, tokens de autenticación o mensajes de error).

### 2. Conectar y Utilizar la Base de Datos

El proyecto ya tiene la configuración básica para conectarse a una base de datos PostgreSQL, pero aún no se está utilizando.

- **Activación:** Se debe utilizar la dependencia `get_session` para inyectar sesiones de base de datos en los endpoints de la API.
- **Modelos de Datos:** Crear los modelos de SQLAlchemy (por ejemplo, `User`) que representen las tablas de la base de datos.
- **Operaciones CRUD:** Implementar las funciones para Crear, Leer, Actualizar y Eliminar registros en la base de datos (por ejemplo, crear un nuevo usuario, buscar uno existente, etc.).

### 3. Despliegue con Docker

Una vez que la funcionalidad principal esté implementada y probada, el paso final será preparar la aplicación para el despliegue en un entorno de producción.

- **Contenerización:** La estrategia recomendada es utilizar Docker para empaquetar la aplicación en un contenedor. Esto asegura que el entorno sea consistente y facilita el despliegue en cualquier proveedor de la nube (AWS, Google Cloud, etc.).
- **Servidor de Producción:** Se utilizará un servidor ASGI de producción como Gunicorn para ejecutar la aplicación dentro del contenedor, garantizando rendimiento y estabilidad.
