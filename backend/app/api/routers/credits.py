from api.dependencies.auth import validate_authenticate_user
from sqlalchemy.exc import SQLAlchemyError
from api.dependencies.db import get_session
from crud.pyme import PymeCrud
from crud.credits import CreditsCrud
from fastapi import APIRouter, Depends, HTTPException, status, Body
from schemas.pyme import PymeCreate, PymeBase
from schemas.credits import CreditsCreate, CreditsSchema
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.user import User
from models.enums import RoleUser
from utils.permissions import check_resource_ownership
from typing import List
import uuid

router = APIRouter()


async def create_pyme(
    db: AsyncSession, 
    current_user: User, 
    pyme_data: PymeBase
):
    """
    Gets the user's existing SME or creates a new one if it doesn't exist.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        pyme_data: Data to create a new SME if necessary
        
    Returns:
        The existing SME or the newly created SME
        
    Raises:
        HTTPException: If there are problems verifying or creating the SME
    """
    pyme_create = PymeCreate(
        **pyme_data.model_dump(),
        user_id=current_user.id
    )
    
    try:
        new_pyme = await PymeCrud(db).create(pyme_create)
        return new_pyme
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating SME associated with credit",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CreditsSchema,
)
async def create_credit(
    credit_create: CreditsCreate = Body(...),
    pyme_data: PymeBase = Body(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Create a new loan. The user must be authenticated.
    If the user does not have an SME, it is automatically created with the information provided.
    If the user already has an SME, it is verified that it matches the pyme_id.
    """
    try:
        # Check if the user has an SME
        existing_pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
        
        # If the user already has an SME
        if existing_pyme:
            # Verify that it matches the pyme_id provided
            if str(existing_pyme.id) != str(credit_create.pyme_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot create loans for another SME. You must use your registered SME.",
                )
        # If the user does not have an SME and data is provided, create one
        elif pyme_data:
            new_pyme = await create_pyme(db, current_user, pyme_data)
            # Update the pyme_id in the credit
            credit_create.pyme_id = new_pyme.id
        # If no Pyme data is provided, error
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide data to create an SME or have an existing SME",
            )
        
        new_credit = await CreditsCrud(db).create(credit_create)
        return new_credit
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating credit",
        )

@router.get(
    "/{credit_id}",
    status_code=status.HTTP_200_OK,
    response_model=CreditsSchema,
)
async def get_credit(
    credit_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Obtain credit using your ID. 
    - ADMIN/SUPERADMIN: Can view any credit
    - USER: Can only view credits from their own SME
    """
    try:
        credit = await CreditsCrud(db).get(credit_id)
        if credit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit with ID {credit_id} not found",
            )

        if current_user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]:
            return credit

        pyme = await PymeCrud(db).get(credit.pyme_id)
        if not pyme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SME associated with this credit not found",
            )

        if await check_resource_ownership(current_user, str(pyme.user_id)):
            return credit
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this credit",
            )
            
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obtaining credit",
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[CreditsSchema],
)
async def get_all_credits(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Get credits based on user role:
    - ADMIN/SUPERADMIN: Can view all credits from all SMEs
    - USER: Can only view credits from their own SME
    """
    try:
        if current_user.role in [RoleUser.ADMIN, RoleUser.SUPERADMIN]:
            credits = await CreditsCrud(db).get_all()
            return list(credits)
        else:
            pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
            if not pyme:
                return []

            try:
                credits = await CreditsCrud(db).get_all_by_attribute("pyme_id", pyme.id)
                return list(credits) 
            except AttributeError as ae:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Data model error: 'pyme_id' attribute does not exist in Credits",
                )
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obtaining credits: {str(e)}",
        )