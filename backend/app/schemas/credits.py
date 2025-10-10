from typing import Optional
from models.enums import StatusCredit
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re
from datetime import datetime


class CreditsBase(BaseModel):
    amount: float
    employees: int
    annual_sales: float
    fiscal_year_closing: str
    total_assets: float
    status: StatusCredit = Field(default=StatusCredit.PENDING)
    pyme_id: UUID
    
    @field_validator("amount", "annual_sales", "total_assets")
    def validate_positive_amount(cls, v, info):
        """Validate that monetary values ​​are positive"""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be a positive value")
        return v
    
    @field_validator("employees")
    def validate_employees(cls, v):
        """Validate that the number of employees is positive"""
        if v <= 0:
            raise ValueError("The number of employees must be positive")
        return v
        
    @field_validator("fiscal_year_closing")
    def validate_fiscal_year(cls, v):
        """Validate that the fiscal year has format YYYY"""
        if not re.match(r'^\d{4}$', v):
            raise ValueError("The fiscal year must have format YYYY")
        year = int(v)
        current_year = datetime.now().year
        if year < 2000 or year > current_year:
            raise ValueError(f"The fiscal year must be between 2000 and {current_year}")
        return v


class CreditsCreate(CreditsBase):
    pass


class CreditsUpdate(BaseModel):
    amount: Optional[float] = None
    employees: Optional[int] = None
    annual_sales: Optional[float] = None
    fiscal_year_closing: Optional[str] = None
    total_assets: Optional[float] = None
    status: Optional[StatusCredit] = None


class CreditsSchema(CreditsBase):
    id: UUID

    class Config:
        from_attributes = True
