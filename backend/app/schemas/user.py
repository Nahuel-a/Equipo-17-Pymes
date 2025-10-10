from typing import Optional
from models.enums import RoleUser
from pydantic import BaseModel, EmailStr, field_validator
import re
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class VerifyResetCode(BaseModel):
    email: EmailStr
    reset_code: str


class PasswordReset(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str
    
    @field_validator("new_password")
    def validate_password(cls, password: str) -> str:
        return PasswordValidator.validate_password(password)


class PasswordValidator:
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Validates that the password meets the following criteria:
        - At least 8 characters long
        - Contains at least one number
        - Contains at least one special character
        
        Args:
            password: The password to validate
            
        Returns:
            str: The validated password
            
        Raises:
            ValueError: If the password doesn't meet the criteria
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 16:
            raise ValueError("Very long password, must be less than 16 characters")
        
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")
        
        return password


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Optional[RoleUser] = RoleUser.USER
    
    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return PasswordValidator.validate_password(password)


class UserSchema(UserBase):
    id: UUID
    role: RoleUser

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return PasswordValidator.validate_password(password)