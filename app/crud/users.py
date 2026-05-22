from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from sqlalchemy import func
from uuid import UUID
from typing import Optional, Tuple
from app import models, schemas
from app.models import Goal, Account
from app.models import Transaction, Goal, Category


class UserCRUD:
    @staticmethod
    def get_all(
            db: Session,
            skip: int = 0,
            limit: int = 100,
            sort: Optional[str] = None,
            order: str = "asc",
            search: Optional[str] = None
    ) -> Tuple[list, int]:
        query = db.query(models.User)

        if search:
            query = query.filter(
                or_(
                    models.User.email.ilike(f"%{search}%"),
                    models.User.full_name.ilike(f"%{search}%")
                )
            )

        total = query.count()

        if sort == "email":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.User.email))
        elif sort == "full_name":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.User.full_name))
        elif sort == "created_at":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.User.created_at))
        else:
            query = query.order_by(models.User.created_at.desc())

        items = query.offset(skip).limit(limit).all()

        return items, total

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create(db: Session, user: schemas.UserCreate) -> models.User:
        existing = UserCRUD.get_by_email(db, user.email)
        if existing:
            raise ValueError(f"User with email '{user.email}' already exists")

        db_user = models.User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(
            db: Session,
            user_id: UUID,
            user_update: schemas.UserUpdate
    ) -> Optional[models.User]:
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != db_user.email:
            existing = UserCRUD.get_by_email(db, update_data["email"])
            if existing:
                raise ValueError(f"User with email '{update_data['email']}' already exists")

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: UUID) -> bool:
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False

        accounts_count = db.query(Account).filter(Account.user_id == user_id).count()
        if accounts_count > 0:
            pass

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def get_user_statistics(db: Session, user_id: UUID) -> dict:

        accounts_count = db.query(Account).filter(Account.user_id == user_id).count()
        categories_count = db.query(Category).filter(Category.user_id == user_id).count()
        active_goals = db.query(Goal).join(Account).filter(
            Account.user_id == user_id,
            Goal.status == "active"
        ).count()

        total_income = db.query(func.sum(Transaction.amount)).join(Account).filter(
            Account.user_id == user_id,
            Transaction.type == "income"
        ).scalar() or 0

        total_expense = db.query(func.sum(Transaction.amount)).join(Account).filter(
            Account.user_id == user_id,
            Transaction.type == "expense"
        ).scalar() or 0

        return {
            "accounts_count": accounts_count,
            "categories_count": categories_count,
            "active_goals_count": active_goals,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(total_income - total_expense)
        }