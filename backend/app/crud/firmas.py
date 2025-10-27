from abstract import BaseCrud
from app.models.models_firmas import DigitalSignature


class SignatureCrud(BaseCrud):
    model = DigitalSignature