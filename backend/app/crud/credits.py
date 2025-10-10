from crud.abstract import BaseCrud
from models.credits import Credits


class CreditsCrud(BaseCrud):
    model = Credits