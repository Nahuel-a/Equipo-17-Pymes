# Plataforma Web de Onboarding de Créditos para PYMES

## Descripción General del Frontend

El frontend ha sido desarrollado como una interfaz de usuario moderna, responsiva y rica en funcionalidades, centrada en proporcionar una experiencia de usuario fluida e intuitiva. La estructura ha sido reorganizada para separar claramente las distintas áreas de la aplicación (página de inicio, flujo de autenticación y dashboard de usuario).

Utiliza HTML5, CSS3 y JavaScript puro (ES6+) para crear una experiencia interactiva sin depender de frameworks externos, lo que garantiza un rendimiento óptimo y un mantenimiento sencillo.

---

## Características Principales

A continuación se detallan las funcionalidades implementadas en el frontend:

### 1. Flujo de Autenticación Completo
Se ha prototipado un ciclo de autenticación completo, simulando la gestión de usuarios a través de `localStorage`.

- **Registro de Usuario (`register-user.html`):**
  - Formulario de registro con validación en tiempo real.
  - **Control de Contraseña Robusta:** Requisitos visuales que el usuario debe cumplir (mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial).

- **Inicio de Sesión (`log-in.html`):**
  - Valida las credenciales del usuario contra los datos guardados.
  - Redirige al `dashboard.html` tras un inicio de sesión exitoso.

- **Recuperación de Contraseña:**
  - Proceso de dos pasos que comienza en `password-user.html`.
  - Permite al usuario establecer una nueva contraseña en `reset-password.html`, aplicando las mismas reglas de seguridad que en el registro.

### 2. Dashboard de Usuario (`dashboard.html`)
- **Ruta Protegida:** Solo accesible después de un inicio de sesión exitoso. Los usuarios no autenticados son redirigidos al login.
- **Vista Conceptual:** Presenta un diseño conceptual de un panel de control donde el usuario puede ver el estado de sus solicitudes de crédito (Aprobado, En Revisión, etc.) y acceder a acciones principales como "Solicitar Nuevo Crédito".
- **Gestión de Sesión:** Muestra el nombre del usuario y un botón para cerrar sesión, limpiando los datos de la sesión simulada.

### 3. Página de Inicio Dinámica (`index.html`)
- **Diseño Profesional:** Una landing page pública con un diseño moderno y responsivo.
- **Secciones Informativas:** Incluye secciones de "Beneficios" y un formulario de "Contacto" estático.

### 4. Mejoras de Experiencia de Usuario (UX)
- **Modo Claro y Oscuro:** Un interruptor en la cabecera permite al usuario cambiar entre un tema visual claro y uno oscuro. La preferencia se guarda en `localStorage` para persistir entre visitas.
- **Soporte Multi-idioma (EN/ES):** Se ha implementado un sistema de traducción simple que permite cambiar el idioma de todo el contenido de la página de inicio entre español e inglés. La selección también se guarda en `localStorage`.
- **Notificaciones Dinámicas:** Se utilizan mensajes "flash" para proporcionar feedback al usuario tras acciones importantes (ej. registro exitoso, cierre de sesión).

---

## Estructura del Frontend

La carpeta `frontend` ha sido reestructurada para mejorar la organización y escalabilidad del código:

```
frontend/
├── static/
│   ├── css/
│   │   ├── home-styles.css     # Estilos exclusivos para la página de inicio (index.html)
│   │   ├── styles.css          # Estilos globales para el flujo de autenticación
│   │   └── dashboard-styles.css # Estilos para el dashboard de usuario
│   ├── js/
│   │   └── app.js              # Lógica JS para autenticación y dashboard
│   └── images/
│       └── ...
└── templates/
    ├── index.html              # Página de inicio pública con tema claro/oscuro e idiomas
    ├── log-in.html             # Formulario de inicio de sesión
    ├── register-user.html      # Formulario de registro con validación de clave
    ├── password-user.html      # Formulario para iniciar la recuperación de clave
    ├── reset-password.html     # Formulario para establecer una nueva clave
    └── dashboard.html          # Dashboard conceptual del usuario
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

Ahora que el frontend está completamente prototipado, los siguientes pasos se centran en conectar la interfaz con una lógica de backend real.

### 1. Implementar los Endpoints de la API

- **Conectar Formularios:** Reemplazar la lógica simulada de `localStorage` en `app.js` y el script de `index.html` con llamadas `fetch` a los endpoints de la API del backend.
- **Rutas a crear/conectar:**
    - `POST /login`: Para manejar el inicio de sesión de usuarios.
    - `POST /register`: Para registrar nuevos usuarios.
    - `POST /password-recovery`: Para gestionar la recuperación de contraseñas.

### 2. Conectar y Utilizar la Base de Datos

- **Activación:** Utilizar la dependencia `get_session` para inyectar sesiones de base de datos en los endpoints de la API.
- **Modelos de Datos:** Crear los modelos de SQLAlchemy (ej. `User`) que representen las tablas de la base de datos.
- **Operaciones CRUD:** Implementar la lógica para gestionar los datos de usuario y solicitudes de crédito.

### 3. Despliegue con Docker

- **Contenerización:** Utilizar Docker para empaquetar la aplicación, garantizando un despliegue consistente y escalable.

