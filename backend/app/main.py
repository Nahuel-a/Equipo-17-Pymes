from fastapi import FastAPI, Request, Form, Body
# from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pathlib import Path
# from email_validator import validate_email, EmailNotValidError
from fastapi.middleware.cors import CORSMiddleware

from api.main import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # domains must be specified in the .env
    allow_origins=["*"],  # Config setting
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(api_router)


# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent.parent

# # Mount static files
# app.mount(
#     "/static",
#     StaticFiles(directory=BASE_DIR / "frontend"),
#     name="static",
# )

# # Setup templates
# templates = Jinja2Templates(directory=BASE_DIR / "frontend")

# # In-memory database for demonstration
# fake_users_db = {}

# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("log-in.html", {"request": request})

# @app.get("/login", response_class=HTMLResponse)
# async def login(request: Request):
#     return templates.TemplateResponse("log-in.html", {"request": request})

# @app.post("/login")
# async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
#     user = fake_users_db.get(email)
#     if not user or not user["password"] == password:
#         return templates.TemplateResponse(
#             "log-in.html",
#             {"request": request, "error": "Email o contraseña incorrectos"},
#         )
#     return templates.TemplateResponse(
#         "dashboard.html", {"request": request, "user": user}
#     )


# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     # This is a protected route, in a real app you would check for a session/token
#     # For the demo, we assume if you get here, you are logged in.
#     # You might want to pass user information to the template.
#     return templates.TemplateResponse("dashboard.html", {"request": request, "user": {"nombre": "Usuario"}})


# @app.get("/register", response_class=HTMLResponse)
# async def register(request: Request):
#     return templates.TemplateResponse("register-user.html", {"request": request})

# @app.post("/register")
# async def register_post(
#     request: Request,
#     nombre: str = Form(...),
#     apellido: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
# ):
#     try:
#         # Validate email
#         email_info = validate_email(email, check_deliverability=False)
#         email = email_info.normalized
#     except EmailNotValidError as e:
#         # You can handle the error, for example, by returning a message to the user
#         return templates.TemplateResponse(
#             "register-user.html",
#             {"request": request, "error": f"Error en email: {str(e)}"},
#         )

#     if email in fake_users_db:
#         return templates.TemplateResponse(
#             "register-user.html",
#             {"request": request, "error": "El email ya está registrado"},
#         )

#     # Store user in the in-memory database
#     # In a real application, you should hash the password
#     fake_users_db[email] = {
#         "nombre": nombre,
#         "apellido": apellido,
#         "password": password,
#     }
#     return RedirectResponse(url="/login", status_code=303)

# @app.post("/check-email")
# async def check_email(email_data: dict = Body(...)):
#     email = email_data.get("email")
#     return JSONResponse({"exists": email in fake_users_db})


# @app.get("/password-recovery", response_class=HTMLResponse)
# async def password_recovery(request: Request):
#     return templates.TemplateResponse("password-user.html", {"request": request})

# @app.post("/password-recovery")
# async def password_recovery_post(request: Request, email: str = Form(...)):
#     # In a real app, you would send an email with a recovery link
#     # For the demo, we'll just redirect to the recovery page
#     return templates.TemplateResponse("recover-account.html", {"request": request, "email": email})

# @app.post("/recover-account")
# async def recover_account_post(request: Request, email: str = Form(...), newPassword: str = Form(...)):
#     if email in fake_users_db:
#         fake_users_db[email]["password"] = newPassword
#     # In a real app, you would show a success message
#     return RedirectResponse(url="/login", status_code=303)


# @app.get("/recover-account", response_class=HTMLResponse)
# async def recover_account(request: Request):
#     return templates.TemplateResponse("recover-account.html", {"request": request})
