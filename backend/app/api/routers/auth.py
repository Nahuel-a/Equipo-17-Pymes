from datetime import timedelta
from api.dependencies.db import get_session
from core.config import get_settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from schemas.user import Token
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils import oauth2
from utils.user import is_authenticate

settings = get_settings()
router = APIRouter()


@router.post("/login/", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
) -> Token:
    """
    Handles a user login and generates an access token if the credentials are correct.
    """
    try:
        # Verify user credentials in the database.
        db_user = await is_authenticate(form_data.username, form_data.password, db)
        
        access_token_expire = timedelta(minutes=int(settings.EXPIRE_TOKEN))
        access_token = await oauth2.create_access_token(
            data={"email": db_user.email}, expires_delta=access_token_expire
        )
        return Token(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        # Rethrows HTTP exceptions already handled in is_authenticate
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="An error occurred during login"
        )
