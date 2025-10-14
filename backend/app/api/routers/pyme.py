from api.dependencies.auth import validate_authenticate_user
from sqlalchemy.exc import SQLAlchemyError
from api.dependencies.db import get_session
from crud.pyme import PymeCrud
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.pyme import PymeSchema, PymeCreate
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.user import User
import uuid

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PymeSchema,
)
async def create_pyme(
    pyme_create: PymeCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Create a new SME. Only an authenticated user can create an SME.
    The SME is associated with the current user, and a user can only have one SME.
    """
    # Check if the user already has an SME
    existing_pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
    if existing_pyme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has a registered SME",
        )

    # If a different user_id is specified than the current user, check permissions
    if pyme_create.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create an SME for another user",
        )
    
    try:
        new_pyme = await PymeCrud(db).create(pyme_create)
        return new_pyme
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating SME",
        )


@router.get(
    "/{pyme_id}",
    status_code=status.HTTP_200_OK,
    response_model=PymeSchema,
)
async def get_pyme(
    pyme_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Obtain an SME by its ID. The user must be authenticated.
    """
    try:
        pyme = await PymeCrud(db).get(pyme_id)
        if pyme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SME with ID {pyme_id} not found",
            )

        # Verify that the current user is the owner of the SME or has special permissions
        if pyme.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this SME",
            )
            
        return pyme
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obtaining SME",
        )