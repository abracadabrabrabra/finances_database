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


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class CategoryCreate(CategoryBase):
    pass  #uid from path


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v


class CategoryResponse(CategoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class UserFinancialSummaryResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    total_accounts: int
    total_transactions: int
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal

    class Config:
        from_attributes = True


class GoalProgressResponse(BaseModel):
    goal_name: str
    email: str
    account_name: str
    target_amount: Decimal
    saved_amount: Decimal
    progress_percent: float
    deadline: Optional[date]
    status: str

    class Config:
        from_attributes = True


class TransactionsPerDayResponse(BaseModel):
    transaction_date: date
    transactions_per_day: int


class UserTransactionStatsResponse(BaseModel):
    email: str
    first_transaction: Optional[date]
    last_transaction: Optional[date]
    smallest_amount: Optional[Decimal]
    largest_amount: Optional[Decimal]


class ImportStatsResponse(BaseModel):
    avg_rows_processed: Optional[float]
    avg_rows_succeeded: Optional[float]
    avg_success_rate: Optional[float]


class AccountBalanceResponse(BaseModel):
    balance_calc: Decimal
    currency: str
    last_transaction_date: Optional[date]


class TransferEligibilityResponse(BaseModel):
    is_possible: bool
    fee: Decimal
    message: str


class TransferRequest(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: str = Field("Money transfer", description="Transfer description")


class TransferResponse(BaseModel):
    success: bool
    message: str
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    fee: Optional[Decimal] = 0