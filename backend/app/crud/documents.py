from crud.abstract import BaseCrud
from models.documents import ApplicationDocuments


class ApplicationDocumentsCrud(BaseCrud):
    model = ApplicationDocuments