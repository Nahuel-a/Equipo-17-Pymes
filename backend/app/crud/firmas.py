from crud.abstract import BaseCrud
from models.models_firmas import DigitalSignature


class SignatureCrud(BaseCrud):
    model = DigitalSignature