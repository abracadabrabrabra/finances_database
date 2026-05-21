from sqlalchemy import (
    Column, String, Integer, Numeric, Date, DateTime,
    ForeignKey, CheckConstraint, UniqueConstraint, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    currency = Column(String(3), nullable=False)
    initial_balance = Column(Numeric(15, 2), default=0)
    type = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uk_accounts_user_name"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="ck_accounts_currency"),
        CheckConstraint("type IN ('checking', 'savings', 'cash', 'credit_card')", name="ck_accounts_type"),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uk_categories_user_name"),
    )


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    deadline = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uk_goals_account_name"),
        CheckConstraint("target_amount > 0", name="ck_goals_target_amount"),
        CheckConstraint("status IN ('active', 'achieved', 'failed')", name="ck_goals_status"),
    )


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255))
    rows_processed = Column(Integer, default=0)
    rows_succeeded = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("rows_processed >= rows_succeeded", name="ck_import_logs_rows"),
        CheckConstraint("rows_succeeded >= 0", name="ck_import_logs_succeeded"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    import_log_id = Column(UUID(as_uuid=True), ForeignKey("import_logs.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(String(10), nullable=False)
    description = Column(Text)
    transaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount"),
        CheckConstraint("type IN ('income', 'expense', 'transfer')", name="ck_transactions_type"),
    )


class ExchangeRateUsd(Base):
    __tablename__ = "exchange_rates_usd"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(20, 10), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("target_currency", "date", name="uk_exchange_rates_currency_date"),
        CheckConstraint("rate > 0", name="ck_exchange_rates_rate"),
        CheckConstraint("target_currency ~ '^[A-Z]{3}$'", name="ck_exchange_rates_currency"),
    )