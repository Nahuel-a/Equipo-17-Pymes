"""CRUD helper for Document model.

This class uses the project's BaseCrud patterns. Add entity-specific
helpers here if needed (e.g. list_by_pyme, search, etc.).
"""

from crud.abstract import BaseCrud
from models.document import Document


class DocumentsCrud(BaseCrud):
    model = Document

    # The BaseCrud parent provides common async create/get/update/delete
    # operations; extend this class only if you need specialized queries.
