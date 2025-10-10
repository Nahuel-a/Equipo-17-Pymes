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
    Crear una nueva Pyme. Solo un usuario autenticado puede crear una Pyme.
    La Pyme está asociada al usuario actual y un usuario solo puede tener una Pyme.
    """
    # Verificar si el usuario ya tiene una Pyme
    existing_pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
    if existing_pyme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario ya tiene una Pyme registrada",
        )
    
    # Si se especificó un user_id diferente al del usuario actual, verificar permisos
    if pyme_create.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede crear una Pyme para otro usuario",
        )
    
    try:
        # Crear la Pyme
        new_pyme = await PymeCrud(db).create(pyme_create)
        return new_pyme
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la Pyme",
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
    Obtener una Pyme por su ID. El usuario debe estar autenticado.
    """
    try:
        pyme = await PymeCrud(db).get(pyme_id)
        if pyme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pyme con ID {pyme_id} no encontrada",
            )
        
        # Verificar que el usuario actual sea el dueño de la Pyme o tenga permisos especiales
        if pyme.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver esta Pyme",
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
            detail="Error al obtener la Pyme",
        )