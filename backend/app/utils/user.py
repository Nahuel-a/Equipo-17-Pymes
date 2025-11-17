from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession
from crud.user import UserCrud
from .password import verify



async def is_authenticate(
    email: str, password: str, db: AsyncSession
):
    """
    Authenticates a user by verifying their email and password.

    Args:
        email (str): The email of the user being authenticated.
        password (str): The plaintext password provided by the user.
        db (AsyncSession): The asynchronous database session.

    Returns:
        user (User | bool): The user object if authentication is successful,
                            or False if it fails.
    """
    try:
        user = await UserCrud(db).get_by_attribute("email", email)
        if user is None:
            # user not found
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email",
                headers={"WWW-Authenticate": "Bearer"},
            )
       
        match, needs_rehash = verify(password, user.password)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Rehash the password if needed
        if needs_rehash:
            user.password = hash(password)
            await db.commit()

        return user

    except SQLAlchemyError as se:
        # Database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while trying to authenticate.",
        )
