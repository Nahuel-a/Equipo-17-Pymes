from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.db import get_session
from api.dependencies.auth import validate_authenticate_user
from models.user import User
from schemas.pyme import PymeSchema  
from schemas.documents import DocumentsIn, DocumentsOut 
from crud.documents import DocumentsCrud 
from utils.firmas import firmar_documento, verificar_firma  # Del código anterior
import uuid
from crud.pyme import PymeCrud  
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
#(prefix="/firmas", tags=["Firmas Digitales"]) # Por si hace falta

@router.post(
    "/{pyme_id}/firmar_documento",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentoOut,
)
async def firmar_documento_para_pyme(
    pyme_id: uuid.UUID = Path(..., description="ID de la Pyme"),
    documento: DocumentsIn,  # Schema para el documento a firmar
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Firma un documento para una Pyme específica. Solo el propietario de la Pyme puede hacerlo.
    """
    # Verifica que el usuario sea el propietario de la Pyme
    pyme = await PymeCrud(db).get(pyme_id)
    if pyme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pyme with ID {pyme_id} not found",
        )
    if pyme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sign documents for this Pyme",
        )
    
    try:
        firma = firmar_documento(documento.contenido)  # Genera la firma
        nuevo_documento = await DocumentsCrud(db).create({  # Asume un método create en tu CRUD
            "pyme_id": pyme_id,
            "contenido": documento.contenido,
            "firma_digital": firma,
        })
        return nuevo_documento
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating and signing document",
        )

@router.get(
    "/{pyme_id}/verificar_documento/{documento_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def verificar_documento_de_pyme(
    pyme_id: uuid.UUID = Path(..., description="ID de la Pyme"),
    documento_id: uuid.UUID = Path(..., description="ID del documento"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Verifica la firma de un documento para una Pyme específica.
    """
    pyme = await PymeCrud(db).get(pyme_id)
    if pyme is None or pyme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to verify this document",
        )
    
    documento = await DocumentsCrud(db).get(documento_id)
    if documento is None or documento.pyme_id != pyme_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento not found for this Pyme",
        )
    
    if verificar_firma(documento.contenido, documento.firma_digital):
        return {"valido": True}
    return {"valido": False}
