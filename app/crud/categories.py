from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, func
from uuid import UUID
from typing import Optional, Tuple
from app import models, schemas
from app.models import Transaction

class CategoryCRUD:
    @staticmethod
    def get_all(
            db: Session,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            sort: Optional[str] = None,
            order: str = "asc",
            search: Optional[str] = None
    ) -> Tuple[list, int]:
        query = db.query(models.Category).filter(models.Category.user_id == user_id)

        if search:
            query = query.filter(models.Category.name.ilike(f"%{search}%"))

        total = query.count()

        if sort == "name":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.Category.name))
        elif sort == "created_at":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.Category.created_at))
        else:
            query = query.order_by(models.Category.name.asc())

        items = query.offset(skip).limit(limit).all()

        return items, total

    @staticmethod
    def get_by_id(db: Session, category_id: UUID, user_id: UUID) -> Optional[models.Category]:
        return db.query(models.Category).filter(
            models.Category.id == category_id,
            models.Category.user_id == user_id
        ).first()

    @staticmethod
    def get_by_name(db: Session, name: str, user_id: UUID) -> Optional[models.Category]:
        return db.query(models.Category).filter(
            models.Category.name == name,
            models.Category.user_id == user_id
        ).first()

    @staticmethod
    def create(db: Session, category: schemas.CategoryCreate, user_id: UUID) -> models.Category:
        existing = CategoryCRUD.get_by_name(db, category.name, user_id)
        if existing:
            raise ValueError(f"Category with name '{category.name}' already exists")

        db_category = models.Category(
            **category.model_dump(),
            user_id=user_id
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update(
            db: Session,
            category_id: UUID,
            user_id: UUID,
            category_update: schemas.CategoryUpdate
    ) -> Optional[models.Category]:
        db_category = CategoryCRUD.get_by_id(db, category_id, user_id)
        if not db_category:
            return None

        update_data = category_update.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != db_category.name:
            existing = CategoryCRUD.get_by_name(db, update_data["name"], user_id)
            if existing:
                raise ValueError(f"Category with name '{update_data['name']}' already exists")

        for field, value in update_data.items():
            setattr(db_category, field, value)

        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete(db: Session, category_id: UUID, user_id: UUID) -> bool:
        db_category = CategoryCRUD.get_by_id(db, category_id, user_id)
        if not db_category:
            return False

        try:
            db.delete(db_category)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            if "foreign key constraint" in str(e).lower() or "restrict" in str(e).lower():
                raise ValueError(
                    f"Cannot delete category '{db_category.name}' because it has associated transactions"
                )
            raise e

    @staticmethod
    def get_statistics(db: Session, user_id: UUID) -> dict:
        total_categories = db.query(func.count(models.Category.id)).filter(
            models.Category.user_id == user_id
        ).scalar() or 0

        categories_with_transactions = db.query(models.Category.id).join(
            Transaction, Transaction.category_id == models.Category.id
        ).filter(
            models.Category.user_id == user_id
        ).distinct().count()

        unused_categories = total_categories - categories_with_transactions

        return {
            "total_categories": total_categories,
            "categories_with_transactions": categories_with_transactions,
            "unused_categories": unused_categories
        }