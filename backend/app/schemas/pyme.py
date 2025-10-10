from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
import re


class PymeBase(BaseModel):
    name_company: str
    cuit: str
    legal_form: str
    activity: str
    corporate_email: EmailStr
    phone_number: str
    country: str
    state: str
    city: str
    address: str
    postal_code: str
    
    @field_validator("cuit")
    def validate_cuit(cls, v):
        """Validate CUIT format (XX-XXXXXXXX-X)"""
        if not re.match(r'^\d{2}-\d{8}-\d{1}$', v):
            raise ValueError("CUIT must have format XX-XXXXXXXX-X")
        return v
    
    @field_validator("phone_number")
    def validate_phone(cls, v):
        """Validate basic phone number format"""
        if not re.match(r'^\+?[\d\s\-\(\)]{8,20}$', v):
            raise ValueError("Phone number is invalid")
        return v


class PymeCreate(PymeBase):
    user_id: UUID


class PymeUpdate(BaseModel):
    name_company: Optional[str] = None
    legal_form: Optional[str] = None
    activity: Optional[str] = None
    corporate_email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None


class PymeSchema(PymeBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


from .credits import CreditsSchema

class PymeDetailSchema(PymeSchema):
    credits: List[CreditsSchema] = []

    class Config:
        from_attributes = True


