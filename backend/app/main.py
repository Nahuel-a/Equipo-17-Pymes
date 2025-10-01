from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "fontend"),
    name="static",
)

# Setup templates
templates = Jinja2Templates(directory=BASE_DIR / "fontend")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("log-in.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("log-in.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register-user.html", {"request": request})

@app.get("/password-recovery", response_class=HTMLResponse)
async def password_recovery(request: Request):
    return templates.TemplateResponse("password-user.html", {"request": request})

@app.get("/recover-account", response_class=HTMLResponse)
async def recover_account(request: Request):
    return templates.TemplateResponse("recover-account.html", {"request": request})
