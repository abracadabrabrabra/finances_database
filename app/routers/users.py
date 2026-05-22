from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=dict)
def get_users(
        page: int = Query(1, ge=1, description="Page num"),
        limit: int = Query(10, ge=1, le=100, description="Records on page"),
        sort: Optional[str] = Query(None, regex="^(email|full_name|created_at)$", description="Field for sort"),
        order: str = Query("asc", regex="^(asc|desc)$", description="Type sort"),
        search: Optional[str] = Query(None, description="Name/email search"),
        db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    items, total = crud.UserCRUD.get_all(
        db=db,
        skip=skip,
        limit=limit,
        sort=sort,
        order=order,
        search=search
    )

    serialized_items = [schemas.UserResponse.model_validate(item) for item in items]

    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse.model_validate(user)


@router.get("/{user_id}/statistics", response_model=dict)
def get_user_statistics(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = crud.UserCRUD.get_user_statistics(db, user_id)
    return {
        "user_id": user_id,
        "user_email": user.email,
        **stats
    }


@router.post("/", response_model=schemas.UserResponse, status_code=201)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    try:
        db_user = crud.UserCRUD.create(db, user)
        return schemas.UserResponse.model_validate(db_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
        user_id: UUID,
        user_update: schemas.UserUpdate,
        db: Session = Depends(get_db)
):
    try:
        db_user = crud.UserCRUD.update(db, user_id, user_update)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return schemas.UserResponse.model_validate(db_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    try:
        deleted = crud.UserCRUD.delete(db, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete user: {str(e)}")
    return None