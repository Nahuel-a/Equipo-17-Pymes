"""API router for digital signatures (documents).

This module exposes two endpoints used to sign and verify documents
for a given Pyme (company). Implementation notes:
- The current implementation uses temporary generated RSA keys for
  demonstration/testing only. In production you must store and manage
  keys securely (KMS, hardware module or database with strict access).
- The endpoints assume FastAPI dependency injection for DB session and
  authentication (`get_session`, `validate_authenticate_user`). Tests
  use dependency overrides to avoid touching the real DB.
"""

from typing import Dict
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_session
from api.dependencies.auth import validate_authenticate_user
from models.user import User
from schemas.documents import DocumentsIn, DocumentsOut
from crud.documents import DocumentsCrud
from utils.firmas import firmar_documento, verificar_firma, generar_par_claves
from crud.pyme import PymeCrud
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(prefix="/firmas", tags=["digital-signatures"])


@router.post(
    "/{pyme_id}/firmar_documento",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentsOut,
)
async def firmar_documento_para_pyme(
    pyme_id: uuid.UUID = Path(..., description="ID of the Pyme"),
    documento: DocumentsIn = Body(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """Sign a document for a Pyme.

    Only the owner of the Pyme (current_user) may sign documents.
    For demo purposes this function generates a temporary key pair,
    signs the document content and stores the signature in the DB.

    Returns the created document (DocumentsOut). For testing the
    public key PEM is attached to the returned payload (NOT for
    production use).
    """
    pyme = await PymeCrud(db).get(pyme_id)
    if pyme is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pyme with ID {pyme_id} not found")
    if pyme.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to sign documents for this Pyme")

    try:
        # Generate a temporary RSA key pair (demo only).
        private_pem, public_pem = generar_par_claves()
        signature_b64 = firmar_documento(documento.contenido, private_pem)

        nuevo_documento = await DocumentsCrud(db).create({
            "pyme_id": pyme_id,
            "contenido": documento.contenido,
            "firma_digital": signature_b64,
        })

        # Build the response from the ORM object (or mapping). We add the
        # public key PEM to support verification in tests.
        result = DocumentsOut.model_validate(nuevo_documento) if hasattr(DocumentsOut, 'model_validate') else DocumentsOut.from_orm(nuevo_documento)
        payload = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        payload["public_key_pem"] = public_pem.decode("utf-8")
        return payload
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating and signing document")


@router.post("/{pyme_id}/verificar_documento/{documento_id}")
async def verificar_documento_de_pyme(
    pyme_id: uuid.UUID = Path(..., description="ID of the Pyme"),
    documento_id: uuid.UUID = Path(..., description="ID of the document"),
    public_key_pem: str = Body(..., description="Public key PEM used to verify"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(validate_authenticate_user),
):
    """Verify the signature of a document for a Pyme.

    Expects the public key PEM (string) to verify the previously stored
    signature. Returns a JSON object {"valido": bool}.
    """
    pyme = await PymeCrud(db).get(pyme_id)
    if pyme is None or pyme.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to verify this document")

    documento = await DocumentsCrud(db).get(documento_id)
    if documento is None or documento.pyme_id != pyme_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found for this Pyme")

    valido = verificar_firma(documento.contenido, documento.firma_digital, public_key_pem.encode("utf-8"))
    return {"valido": valido}
