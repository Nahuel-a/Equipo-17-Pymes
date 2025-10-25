from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.db import get_session
from api.dependencies.auth import validate_authenticate_user
from models.user import User
from schemas.pyme import PymeSchema  
#from schemas.documents import DocumentsIn, DocumentsOut  
#from crud.documents import DocumentsCrud 
from utils.firmas import sign_document, verify_signature  # Del código anterior (renombrada a inglés)
import uuid
from crud.pyme import PymeCrud  
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.firmas import SignatureCreate, SignatureOut
#Hay que traer desde development el documentscrud y documentsschemas
# Los from que estan comentados hay que activarlos cuando se pongan el eschemas y el crud
router = APIRouter()
#(prefix="/firmas", tags=["Firmas Digitales"]) # Por si hace falta

@router.post(
    "/{pyme_id}/sign_document",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentsOut,
)
async def sign_document_for_pyme(
    pyme_id: uuid.UUID = Path(..., description="ID de la Pyme"),
    document: DocumentsIn,  # Schema for the document to be signed
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Sign a document for a specific SME. Only the SME owner can do this.
    """
   # Verify that the user is the owner of the SME
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
    # Sign the document
    # Use the incoming Pydantic model `document` which contains the content
    try:
        # sign_document is synchronous in this utilities module
        # Support both possible field names coming from other modules: 'content' or 'contenido'
        content_value = getattr(document, 'content', None)
        if content_value is None:
            content_value = getattr(document, 'contenido', None)
        if content_value is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document payload must contain 'content'",
            )

        sign = sign_document(content_value)

        # Ensure DocumentsCrud.create is an async method; if it's sync, adapt accordingly
        new_document = await DocumentsCrud(db).create({
            "pyme_id": pyme_id,
            "content": content_value,
            "digital_signature": sign,
        })

        return new_document
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating and signing document",
        )

@router.get(
    "/{pyme_id}/verificar_documento/{documento_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def verify_SME_document(
    pyme_id: uuid.UUID = Path(..., description="ID de la Pyme"),
    document_id: uuid.UUID = Path(..., description="ID del documento"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """
    Verify the signature of a document for a specific SME.
    """
    pyme = await PymeCrud(db).get(pyme_id)
    if pyme is None or pyme.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to verify this document",
        )

    document = await DocumentsCrud(db).get(document_id)
    if document is None or document.pyme_id != pyme_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento not found for this Pyme",
        )

    # Support both possible field names on the stored document: 'content' or 'contenido',
    # and for the signature 'digital_signature' or 'signature'.
    stored_content = getattr(document, 'content', None) or getattr(document, 'contenido', None)
    stored_signature = getattr(document, 'digital_signature', None) or getattr(document, 'signature', None)

    if stored_content is None or stored_signature is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored document lacks content or signature fields",
        )

    if verify_signature(stored_content, stored_signature):
        return {"valid": True}
    return {"valid": False}
