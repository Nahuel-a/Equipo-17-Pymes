INSTALLED_APPS = [
    # ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from jose import jwt
from datetime import datetime, timedelta, timezone

app = FastAPI()

# Configura con tus datos
GOOGLE_CLIENT_ID = "TU_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "TU_CLIENT_SECRET"
JWT_SECRET = "TU_SECRETO_JWT"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/login/google", response_model=TokenResponse)
def login_google(token_id: str):
    # Verifica token de Google
    resp = requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={token_id}"
    )

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token inválido")

    google_token_info = resp.json()

    # Validar audiencia
    if google_token_info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Token inválido")

    #Validar emisor
    if google_token_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    # Validar expiración del token de Google
    exp = int(google_token_info.get("exp", 0))
    if datetime.now(timezone.utc).timestamp() > exp:
        raise HTTPException(status_code=400, detail="Token expirado")
    
    # Aquí puedes crear o actualizar usuario en Django vía API o base de datos compartida

    # Crea JWT propio para tu app
    payload = {
        "sub": google_token_info["sub"],
        "email": google_token_info["email"],
        "exp": int(datetime.now(timezone.utc)) + timedelta(minutes=JWT_EXPIRATION_MINUTES).timestamp(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token}
