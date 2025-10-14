# Equipo-17-Pymes: CreditBusters

Plataforma Web de Onboarding de Créditos para PYMES.

## Estado Actual del Proyecto

A fecha actual, el proyecto ha alcanzado un hito clave: la implementación de un **sistema de autenticación de usuarios completamente funcional**. Este sistema sienta las bases para un acceso seguro y único para cada PYME, cumpliendo con el objetivo principal de la primera demo.

- **Autenticación de Usuarios:**
  - **Registro:** Los nuevos usuarios pueden registrarse a través de un formulario que valida la información en tiempo real.
  - **Inicio de Sesión:** Los usuarios existentes pueden acceder a su cuenta.
  - **Recuperación de Contraseña:** Se ha implementado un flujo para que los usuarios puedan restablecer su contraseña.

- **Validación en el Frontend:**
  - **Verificación de Email:** El formulario de registro comprueba si el correo electrónico ya está en uso.
  - **Sugerencia de Contraseña Segura:** Se guía al usuario para que elija una contraseña robusta mediante un regex.

- **Backend (FastAPI):**
  - Sirve todas las vistas del frontend y gestiona la lógica de negocio.
  - Utiliza una **base de datos en memoria** para una demostración rápida y funcional, que puede ser fácilmente reemplazada por una base de datos persistente.

- **Branding:**
  - Todas las vistas han sido actualizadas con el nombre corporativo **CreditBusters**.

---

## Estructura del Proyecto

```
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/
│   │   │   │   └── db.py
│   │   │   └── routers/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── crud/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── test/
│   │   └── utils/
│   │       ├── contraseñas.py
│   │       └── logInGoogle.py
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   └── script.py.mako
│   │   ├── __init__.py
│   │   ├── alembic.ini
│   │   └── main.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
│
└── fontend/
    ├── app.js
    ├── dashboard.html
    ├── log-in.html
    ├── password-user.html
    ├── recover-account.html
    ├── register-user.html
    └── styles.css
```

---

## Funcionalidades de la Demo

Para esta demostración, se han implementado los siguientes endpoints en `backend/app/main.py`:

- **GET /**: Página de inicio (login).
- **GET /login**: Página de inicio de sesión.
- **POST /login**: Maneja la autenticación del usuario.
- **GET /register**: Página de registro de usuario.
- **POST /register**: Maneja la creación de un nuevo usuario.
- **POST /check-email**: Verifica si un email ya existe (para validación en tiempo real).
- **GET /password-recovery**: Página para iniciar la recuperación de contraseña.
- **POST /password-recovery**: Maneja la solicitud de recuperación.
- **GET /recover-account**: Página para establecer una nueva contraseña.
- **POST /recover-account**: Maneja el cambio de contraseña.
- **GET /dashboard**: Panel de usuario al que se accede después de un inicio de sesión exitoso.

Toda la información de los usuarios se almacena temporalmente en una base de datos en memoria (`fake_users_db`).

---

## Cómo Ejecutar el Proyecto

### Entorno de Desarrollo

Para ejecutar la aplicación en tu entorno local:

1.  **Navega al directorio del backend:**
    ```bash
    cd backend
    ```

2.  **Crea el entorno virtual e instala las dependencias:**
    ```bash
    poetry install
    ```

3.  **Lanza la aplicación:**
    El servidor se iniciará con recarga automática en `http://127.0.0.1:8000`.
    ```bash
    poetry run python -m uvicorn app.main:app --reload
    ```

### Entorno de Producción (Despliegue)

Para desplegar la aplicación en un servidor de producción:

1.  **Instala las dependencias de producción:**
    ```bash
    poetry install --no-dev
    ```

2.  **Inicia el servidor con Gunicorn:**
    Gunicorn gestionará la aplicación de forma robusta.
    ```bash
    poetry run gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
    ```

---

## Objetivos Finales y Siguientes Pasos

Con la base de la autenticación ya establecida, los próximos objetivos son:

1.  **Implementar la Lógica de Backend Real:**
    - **Conexión a PostgreSQL:** Reemplazar la base de datos en memoria con una conexión real a PostgreSQL, utilizando los modelos de SQLAlchemy y Alembic para las migraciones.
    - **Pruebas Unitarias y de Integración:** Asegurar que la lógica del backend sea robusta y fiable.

2.  **Integrar las Funcionalidades del Sprint 1:**
    - **Formulario de Solicitud de Crédito:** Desarrollar el formulario dinámico.
    - **Carga de Documentos:** Implementar la subida de archivos.
    - **Panel de Administración:** Crear la interfaz para que los operadores de CreditBusters gestionen las solicitudes.

3.  **Migrar a Docker:**
    - **Contenerización:** Crear un `Dockerfile` para empaquetar la aplicación, facilitando un despliegue consistente y escalable en cualquier entorno de nube.