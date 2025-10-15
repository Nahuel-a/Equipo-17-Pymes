from api.dependencies.auth import validate_authenticate_user
from sqlalchemy.exc import SQLAlchemyError
from api.dependencies.db import get_session
from crud.user import UserCrud
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas.user import UserSchema, UserCreate, PasswordResetRequest, VerifyResetCode, PasswordReset
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils.password import hash
from utils.reset_password import generate_password_reset_code, verify_password_reset_code, clear_password_reset_code
from utils.email_service import email_service
import logging
import uuid

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
    If it doesn't exist, creates the user with a hashed password.
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

@router.get(
    "/{user_id}/",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
)
async def get_user_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    curret_user: str = Depends(validate_authenticate_user),
):
    """
    Retrieves a user by its ID. Checks that the user exists in the database.
    """
    try:
        user = await UserCrud(db).get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not exist",
            )
        return user

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


async def send_reset_code_email(email: str, reset_code: str):
    """
    Send password reset code via email using SendGrid service.
    """
    try:        
        success = await email_service.send_password_reset_email(email, reset_code)
        
        if success:
            logging.info(f"Password reset email sent successfully to {email}")
        else:
            logging.error(f"Failed to send password reset email to {email}")
            
    except Exception as e:
        logging.error(f"Error sending password reset email to {email}: {str(e)}")
        # En caso de error, también log del código para debugging (remover en producción)
        logging.info(f"Password reset code for {email}: {reset_code}")


@router.post("/password-reset-request/", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
):
    """
    A code is requested to reset the password. 
    This code is sent to the user's email address, if they have one.
    """
    user = await UserCrud(db).get_by_attribute("email", reset_request.email)

    # Always respond with OK even if the user does not exist (for security)
    if not user:
        return {"message": "If your email is registered, you will receive a recovery code"}
    
    # Generate and send recovery code
    reset_code = await generate_password_reset_code(reset_request.email)

    # Add email sending task to background tasks
    background_tasks.add_task(send_reset_code_email, reset_request.email, reset_code)

    return {"message": "If your email is registered, you will receive a recovery code"}


@router.post("/verify-reset-code/", status_code=status.HTTP_200_OK)
async def verify_reset_code(
    verify_request: VerifyResetCode,
    db: AsyncSession = Depends(get_session),
):
    """
    Verifies if the recovery code is valid.
    """
    # Check if the user exists
    user = await UserCrud(db).get_by_attribute("email", verify_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check the code
    is_valid = await verify_password_reset_code(verify_request.email, verify_request.reset_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code",
        )

    return {"message": "Code verified successfully"}


@router.post("/reset-password/", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_session),
):
    """
    Resets the user's password using a valid recovery code.
    """
    # Check if the user exists
    user = await UserCrud(db).get_by_attribute("email", reset_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check the code
    is_valid = await verify_password_reset_code(reset_data.email, reset_data.reset_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code",
        )
    
    try:
        # Update the password
        hashed_password = await hash(reset_data.new_password)
        await UserCrud(db).update_attribute(user.id, "password", hashed_password)

        # Clear the recovery code
        await clear_password_reset_code(reset_data.email)

        return {"message": "Password updated successfully"}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating password",
        )