from api.dependencies.auth import validate_authenticate_user
from sqlalchemy.exc import SQLAlchemyError
from api.dependencies.db import get_session
from crud.pyme import PymeCrud
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.pyme import PymeSchema, PymeCreate
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.user import User
from models.enums import RoleUser
from utils.permissions import check_resource_ownership
from typing import List
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
    - ADMIN/SUPERADMIN: Can view any SME
    - USER: Can only view their own SME
    """
    try:
        pyme = await PymeCrud(db).get(pyme_id)
        if pyme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SME with ID {pyme_id} not found",
            )

        if current_user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]:
            return pyme
        elif await check_resource_ownership(current_user, str(pyme.user_id)):
            return pyme
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this SME",
            )
            
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


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[PymeSchema],
)
async def get_all_pymes(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Get SMEs based on user role:
    - ADMIN/SUPERADMIN: Can view all SMEs
    - USER: Can only view their own SME
    """
    try:
        if current_user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]:
            pymes = await PymeCrud(db).get_all()
            return list(pymes)
        else:
            pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
            return [pyme] if pyme else []
            
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obtaining SMEs",
        )