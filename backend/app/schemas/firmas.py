from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class SignatureBase(BaseModel):
    """Base schema shared between create/update/output for a digital signature.

    Field names are in English to keep project-wide consistency.
    """
    signature: Optional[str] = Field(None, description="Signature encoded string (e.g. base64)")
    signature_date: Optional[datetime] = Field(None, description="UTC timestamp when the signature was created")
    document_id: int = Field(..., description="ID of the related document")

    @field_validator("signature")
    def validate_signature(cls, value):
        """If provided, ensure the signature looks like a base64-like string (basic check)."""
        if value is None:
            return value
        # Basic sanity check for base64-like content (allows padding = and common chars)
        if not re.match(r'^[A-Za-z0-9+/=\n\r]+$', value):
            raise ValueError("signature must be a base64-like encoded string")
        return value


class SignatureCreate(SignatureBase):
    """Schema used when creating a new signature. `signature` is required."""
    signature: str = Field(..., description="Signature encoded string (base64)")


class SignatureUpdate(BaseModel):
    """Schema for partial updates on a signature record."""
    signature: Optional[str] = None
    signature_date: Optional[datetime] = None


class SignatureOut(SignatureBase):
    """Schema returned by the API when reading signature records."""
    id: int

    class Config:
        from_attributes = True
