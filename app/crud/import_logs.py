from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, and_, func
from uuid import UUID
from typing import Optional, Tuple
from app import models, schemas
from app.models import Transaction


class ImportLogCRUD:
    @staticmethod
    def get_all(
            db: Session,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            sort: Optional[str] = None,
            order: str = "asc",
            search: Optional[str] = None,
            min_processed: Optional[int] = None,
            has_error: Optional[bool] = None
    ) -> Tuple[list, int]:
        query = db.query(models.ImportLog).filter(models.ImportLog.user_id == user_id)

        if search:
            query = query.filter(models.ImportLog.file_name.ilike(f"%{search}%"))

        if min_processed is not None:
            query = query.filter(models.ImportLog.rows_processed >= min_processed)

        if has_error is not None:
            if has_error:
                query = query.filter(models.ImportLog.error_message.isnot(None))
            else:
                query = query.filter(models.ImportLog.error_message.is_(None))

        total = query.count()

        if sort == "file_name":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.ImportLog.file_name))
        elif sort == "rows_processed":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.ImportLog.rows_processed))
        elif sort == "rows_succeeded":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.ImportLog.rows_succeeded))
        elif sort == "created_at":
            order_func = asc if order == "asc" else desc
            query = query.order_by(order_func(models.ImportLog.created_at))
        else:
            query = query.order_by(models.ImportLog.created_at.desc())
        items = query.offset(skip).limit(limit).all()

        return items, total

    @staticmethod
    def get_by_id(db: Session, log_id: UUID, user_id: UUID) -> Optional[models.ImportLog]:
        return db.query(models.ImportLog).filter(
            models.ImportLog.id == log_id,
            models.ImportLog.user_id == user_id
        ).first()

    @staticmethod
    def create(db: Session, log: schemas.ImportLogCreate) -> models.ImportLog:
        if log.rows_succeeded > log.rows_processed:
            raise ValueError("rows_succeeded cannot be greater than rows_processed")

        db_log = models.ImportLog(**log.model_dump())
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def update(
            db: Session,
            log_id: UUID,
            user_id: UUID,
            log_update: schemas.ImportLogUpdate
    ) -> Optional[models.ImportLog]:
        db_log = ImportLogCRUD.get_by_id(db, log_id, user_id)
        if not db_log:
            return None

        update_data = log_update.model_dump(exclude_unset=True)

        if "rows_succeeded" in update_data and "rows_processed" in update_data:
            if update_data["rows_succeeded"] > update_data["rows_processed"]:
                raise ValueError("rows_succeeded cannot be greater than rows_processed")
        elif "rows_succeeded" in update_data:
            new_succeeded = update_data["rows_succeeded"]
            if new_succeeded > db_log.rows_processed:
                raise ValueError(
                    f"rows_succeeded ({new_succeeded}) cannot be greater than rows_processed ({db_log.rows_processed})")
        elif "rows_processed" in update_data:
            new_processed = update_data["rows_processed"]
            if db_log.rows_succeeded > new_processed:
                raise ValueError(
                    f"rows_succeeded ({db_log.rows_succeeded}) cannot be greater than rows_processed ({new_processed})")

        for field, value in update_data.items():
            setattr(db_log, field, value)

        db.commit()
        db.refresh(db_log)
        return db_log

    @staticmethod
    def delete(db: Session, log_id: UUID, user_id: UUID) -> bool:
        db_log = ImportLogCRUD.get_by_id(db, log_id, user_id)
        if not db_log:
            return False

        transactions_count = db.query(Transaction).filter(
            Transaction.import_log_id == log_id
        ).count()

        if transactions_count > 0:
            pass

        db.delete(db_log)
        db.commit()
        return True

    @staticmethod
    def get_statistics(db: Session, user_id: UUID) -> dict:
        total_imports = db.query(func.count(models.ImportLog.id)).filter(
            models.ImportLog.user_id == user_id
        ).scalar() or 0

        total_rows_processed = db.query(func.sum(models.ImportLog.rows_processed)).filter(
            models.ImportLog.user_id == user_id
        ).scalar() or 0

        total_rows_succeeded = db.query(func.sum(models.ImportLog.rows_succeeded)).filter(
            models.ImportLog.user_id == user_id
        ).scalar() or 0

        failed_imports = db.query(func.count(models.ImportLog.id)).filter(
            models.ImportLog.user_id == user_id,
            models.ImportLog.error_message.isnot(None)
        ).scalar() or 0

        success_rate = (total_rows_succeeded / total_rows_processed * 100) if total_rows_processed > 0 else 0

        return {
            "total_imports": total_imports,
            "total_rows_processed": total_rows_processed,
            "total_rows_succeeded": total_rows_succeeded,
            "failed_imports": failed_imports,
            "success_rate": round(success_rate, 2)
        }