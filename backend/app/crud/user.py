from crud.abstract import BaseCrud
from models.user import User


class UserCrud(BaseCrud):
    model = User