from abstract import BaseCrud
from app.models.documents import ApplicationDocument


class ApplicationDocumentCrud(BaseCrud):
    model = ApplicationDocument