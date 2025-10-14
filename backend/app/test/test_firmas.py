import asyncio
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import firmas as firmas_router
from app.utils.firmas import generar_par_claves, firmar_documento, verificar_firma


class DummyPyme:
    def __init__(self, id, user_id):
        self.id = id
        self.user_id = user_id


class DummyDocumento:
    def __init__(self, id, pyme_id, contenido, firma_digital):
        self.id = id
        self.pyme_id = pyme_id
        self.contenido = contenido
        self.firma_digital = firma_digital


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(firmas_router.router, prefix="/api")
    return app


@pytest.mark.asyncio
async def test_firma_y_verificacion(app):
    # Preparar claves y contenido
    private_pem, public_pem = generar_par_claves()
    contenido = "contenido de prueba"
    firma = firmar_documento(contenido, private_pem)

    # Mockear PymeCrud.get y DocumentsCrud.create/get mediante monkeypatch
    pyme_id = uuid.uuid4()
    user_id = uuid.uuid4()
    documento_id = uuid.uuid4()

    async def fake_get_pyme(self, _id):
        return DummyPyme(pyme_id, user_id)

    async def fake_create_document(self, data):
        return DummyDocumento(documento_id, data["pyme_id"], data["contenido"], data["firma_digital"])

    async def fake_get_document(self, _id):
        return DummyDocumento(documento_id, pyme_id, contenido, firma)

    # Reemplazar las clases usadas por el router por fakes que no usan DB
    class FakePymeCrud:
        def __init__(self, session=None):
            pass

        async def get(self, _id):
            return await fake_get_pyme(None, _id)

    class FakeDocumentsCrud:
        def __init__(self, session=None):
            pass

        async def create(self, data):
            return await fake_create_document(None, data)

        async def get(self, _id):
            return await fake_get_document(None, _id)

    # Parchar las referencias en el módulo del router para que el código use nuestros fakes
    firmas_router.PymeCrud = FakePymeCrud
    firmas_router.DocumentsCrud = FakeDocumentsCrud

    # Mockear dependencia de usuario autenticado devolviendo objeto con id=user_id
    class CurrentUser:
        id = user_id

    async def fake_get_session():
        class DummySession:
            pass
        yield DummySession()

    async def fake_current_user_dep():
        return CurrentUser()

    # Registrar overrides de dependencias para que FastAPI use nuestras fakes
    from app.api.dependencies.db import get_session as real_get_session
    from app.api.dependencies.auth import validate_authenticate_user as real_validate_auth

    app.dependency_overrides[real_get_session] = fake_get_session
    app.dependency_overrides[real_validate_auth] = fake_current_user_dep

    # Llamar a las funciones del router directamente para evitar la capa HTTP y las dependencias de FastAPI
    from app.schemas.documents import DocumentsIn

    documento_in = DocumentsIn(contenido=contenido)

    # Llamar a la función async que firma el documento
    # Parche temporal para aceptar objetos simples (DummyDocumento) con Pydantic v2
    from app.schemas.documents import DocumentsOut

    # Guardar el model_validate original y envolverlo para aceptar instancias
    original_model_validate = getattr(DocumentsOut, "model_validate", None)

    def fake_model_validate(obj):
        # Si nos pasan un objeto que no es dict, convertirlo a mapping simple
        if not isinstance(obj, dict):
            obj = {
                "id": getattr(obj, "id", None),
                "pyme_id": getattr(obj, "pyme_id", None),
                "contenido": getattr(obj, "contenido", None),
                "firma_digital": getattr(obj, "firma_digital", None),
                "fecha_firma": getattr(obj, "fecha_firma", None),
            }
        # Llamar al validador original con el dict resultante
        if original_model_validate is not None:
            return original_model_validate(obj)
        # En entornos donde no exista model_validate, fallback a from_orm si está disponible
        return DocumentsOut.from_orm(obj) if hasattr(DocumentsOut, "from_orm") else DocumentsOut(**obj)

    firmas_router.DocumentsOut.model_validate = fake_model_validate

    nuevo_doc = await firmas_router.firmar_documento_para_pyme(pyme_id=pyme_id, documento=documento_in, db=None, current_user=CurrentUser())
    # nuevo_doc puede ser un dict o un Pydantic model según implementación
    # Si es Pydantic model, convertir a dict
    if hasattr(nuevo_doc, "dict"):
        nuevo_doc = nuevo_doc.dict()

    assert nuevo_doc["contenido"] == contenido
    assert "firma_digital" in nuevo_doc
    assert "public_key_pem" in nuevo_doc

    # Llamar a la función async que verifica el documento
    ver_resp = await firmas_router.verificar_documento_de_pyme(pyme_id=pyme_id, documento_id=documento_id, public_key_pem=public_pem.decode('utf-8'), db=None, current_user=CurrentUser())
    assert isinstance(ver_resp, dict)
    assert ver_resp["valido"] is True
