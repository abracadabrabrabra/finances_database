from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class UserBase(BaseModel):
    email: str = Field(..., max_length=255, description="User email")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserCreate(UserBase):
    password_hash: str = Field(..., min_length=6, description="Password hash")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=100)
    password_hash: Optional[str] = Field(None, min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if "@" not in v or "." not in v:
                raise ValueError("Invalid email format")
            return v.lower().strip()
        return v


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportLogBase(BaseModel):
    file_name: Optional[str] = Field(None, max_length=255, description="Log filename")
    rows_processed: int = Field(0, ge=0, description="Total strings")
    rows_succeeded: int = Field(0, ge=0, description="Succeeded strings")
    error_message: Optional[str] = Field(None, description="Error msg")

class ImportLogCreate(ImportLogBase):
    user_id: UUID = Field(..., description="User ID")

class ImportLogUpdate(BaseModel):
    file_name: Optional[str] = Field(None, max_length=255)
    rows_processed: Optional[int] = Field(None, ge=0)
    rows_succeeded: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None

class ImportLogResponse(ImportLogBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True