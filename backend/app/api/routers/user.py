#from api.dependencies.auth import validate_authenticate_user
from api.dependencies.db import get_session
from crud.user import UserCrud
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user import UserSchema, UserCreate
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils.password import hash

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new user. Checks if the user already exists by email.
    If it doesn't exist, creates the user and automatically assigns a MyCourses to it.
    """
    exist_user = await UserCrud(db).get_by_attribute("email", user_create.email)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail=f"User with email '{exist_user.email}' is already registered",
        )
    hashed_password = await hash(user_create.password)
    user_create.password = hashed_password
    new_user = await UserCrud(db).create(user_create)
    return new_user