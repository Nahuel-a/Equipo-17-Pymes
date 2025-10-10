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
    # # Verificar si el usuario ya tiene una Pyme
    # existing_pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
    
    # if existing_pyme:
    #     # El usuario ya tiene una Pyme
    #     return existing_pyme
    
    # # El usuario no tiene una Pyme, crear una nueva
    # if pyme_id:
    #     # Verificar si la Pyme con este ID ya existe
    #     pyme = await PymeCrud(db).get(pyme_id)
    #     if pyme:
    #         # Si existe y no tiene usuario asignado, asignarla
    #         if not pyme.user_id:
    #             await PymeCrud(db).update_attribute(pyme.id, "user_id", current_user.id)
    #             return pyme
    #         else:
    #             # Si ya tiene usuario asignado, error
    #             raise HTTPException(
    #                 status_code=status.HTTP_403_FORBIDDEN,
    #                 detail="La Pyme proporcionada ya está asignada a otro usuario",
    #             )
    
    # Crear una nueva Pyme
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
    Crear un nuevo crédito. El usuario debe estar autenticado.
    Si el usuario no tiene una Pyme, se crea automáticamente con los datos proporcionados.
    Si el usuario ya tiene una Pyme, se verifica que corresponda con la pyme_id.
    """
    try:
        # Verificar si el usuario tiene una Pyme
        existing_pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
        
        # Si el usuario ya tiene una Pyme
        if existing_pyme:
            # Verificar que corresponda con la pyme_id proporcionada
            if str(existing_pyme.id) != str(credit_create.pyme_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No puede crear créditos para otra Pyme. Debe usar su Pyme registrada.",
                )
        # Si el usuario no tiene una Pyme y se proporcionaron datos, crear una
        elif pyme_data:
            new_pyme = await create_pyme(db, current_user, pyme_data)
            # Actualizar la pyme_id en el crédito
            credit_create.pyme_id = new_pyme.id
        # Si no se proporcionaron datos de Pyme, error
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar datos para crear una Pyme o tener una Pyme existente",
            )
        
        # Crear el crédito
        new_credit = await CreditsCrud(db).create(credit_create)
        return new_credit
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el crédito",
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
    Obtener un crédito por su ID. El usuario debe estar autenticado y ser el dueño de la Pyme asociada al crédito.
    """
    try:
        credit = await CreditsCrud(db).get(credit_id)
        if credit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crédito con ID {credit_id} no encontrado",
            )
        
        # Obtener la Pyme asociada al crédito
        pyme = await PymeCrud(db).get(credit.pyme_id)
        
        # Verificar que el usuario actual sea el dueño de la Pyme
        if pyme.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver este crédito",
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
            detail="Error al obtener el crédito",
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
    Obtener todos los créditos asociados a la Pyme del usuario autenticado.
    Si el usuario no tiene una Pyme, devuelve una lista vacía.
    """
    try:
        # Verificar si el usuario tiene una Pyme
        pyme = await PymeCrud(db).get_by_attribute("user_id", current_user.id)
        if not pyme:
            return []
        
        # Obtener todos los créditos de esa Pyme
        try:
            credits = await CreditsCrud(db).get_all_by_attribute("pyme_id", pyme.id)
            return list(credits)  # Aseguramos que se devuelva una lista
        except AttributeError as ae:
            # En caso de que el modelo Credits no tenga el atributo pyme_id (lo cual no debería pasar)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error en el modelo de datos: el atributo 'pyme_id' no existe en Credits",
            )
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los créditos: {str(e)}",
        )