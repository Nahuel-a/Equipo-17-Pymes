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
from typing import List
import uuid

router = APIRouter()


async def create_pyme(
    db: AsyncSession, 
    current_user: User, 
    pyme_data: PymeBase
):
    """
    Obtiene la Pyme existente del usuario o crea una nueva si no existe.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        pyme_data: Datos para crear una nueva Pyme si es necesario
        pyme_id: ID opcional de la Pyme
        
    Returns:
        La Pyme existente o la nueva Pyme creada
        
    Raises:
        HTTPException: Si hay problemas al verificar o crear la Pyme
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
            detail="Error al crear la Pyme asociada al crédito",
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
    Obtain credit using your ID. The user must be authenticated and the owner of the SME associated with the credit.
    """
    try:
        credit = await CreditsCrud(db).get(credit_id)
        if credit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit with ID {credit_id} not found",
            )

        # Get the SME associated with the credit
        pyme = await PymeCrud(db).get(credit.pyme_id)

        # Verify that the current user is the owner of the SME
        if pyme.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this credit",
            )
            
        return credit
        
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
    Obtain all credits associated with the authenticated user's SME.
    If the user does not have an SME, return an empty list.
    """
    try:
        # Check if the user has an SME
        pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
        if not pyme:
            return []

        # Get all credits from that SME
        try:
            credits = await CreditsCrud(db).get_all_by_attribute("pyme_id", pyme.id)
            return list(credits) 
        except AttributeError as ae:
            # In case the Credits model does not have the pyme_id attribute (which shouldn't happen)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data model error: 'pyme_id' attribute does not exist in Credits",
            )
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obtaining credits: {str(e)}",
        )