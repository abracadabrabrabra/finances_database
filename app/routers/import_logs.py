from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users/{user_id}/import-logs", tags=["Import Logs"])


@router.get("/", response_model=dict)
def get_import_logs(
        user_id: UUID,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        sort: Optional[str] = Query(None, regex="^(file_name|rows_processed|rows_succeeded|created_at)$"),
        order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None),
        min_processed: Optional[int] = Query(None, ge=0),
        has_error: Optional[bool] = Query(None),
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skip = (page - 1) * limit
    items, total = crud.ImportLogCRUD.get_all(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        sort=sort,
        order=order,
        search=search,
        min_processed=min_processed,
        has_error=has_error
    )

    serialized_items = [schemas.ImportLogResponse.model_validate(item) for item in items]

    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }


@router.get("/statistics", response_model=dict)
def get_import_statistics(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = crud.ImportLogCRUD.get_statistics(db, user_id)
    return stats


@router.get("/{log_id}", response_model=schemas.ImportLogResponse)
def get_import_log(
        user_id: UUID,
        log_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log = crud.ImportLogCRUD.get_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=404, detail="Import log not found")
    return schemas.ImportLogResponse.model_validate(log)


@router.post("/", response_model=schemas.ImportLogResponse, status_code=201)
def create_import_log(
        user_id: UUID,
        log: schemas.ImportLogCreate,
        db: Session = Depends(get_db)
):
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        log.user_id = user_id

        db_log = crud.ImportLogCRUD.create(db, log)
        return schemas.ImportLogResponse.model_validate(db_log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create import log: {str(e)}")


@router.put("/{log_id}", response_model=schemas.ImportLogResponse)
def update_import_log(
        user_id: UUID,
        log_id: UUID,
        log_update: schemas.ImportLogUpdate,
        db: Session = Depends(get_db)
):
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db_log = crud.ImportLogCRUD.update(db, log_id, user_id, log_update)
        if not db_log:
            raise HTTPException(status_code=404, detail="Import log not found")
        return schemas.ImportLogResponse.model_validate(db_log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{log_id}", status_code=204)
def delete_import_log(
        user_id: UUID,
        log_id: UUID,
        db: Session = Depends(get_db)
):
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        deleted = crud.ImportLogCRUD.delete(db, log_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Import log not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete import log: {str(e)}")
    return None