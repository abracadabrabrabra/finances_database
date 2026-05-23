from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users/{user_id}/categories", tags=["Categories"])


@router.get("/", response_model=dict)
def get_categories(
        user_id: UUID,
        page: int = Query(1, ge=1, description="Page num"),
        limit: int = Query(10, ge=1, le=100, description="Records on page"),
        sort: Optional[str] = Query(None, regex="^(name|created_at)$", description="Sort field"),
        order: str = Query("asc", regex="^(asc|desc)$", description="Sort type"),
        search: Optional[str] = Query(None, description="Name search"),
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skip = (page - 1) * limit
    items, total = crud.CategoryCRUD.get_all(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        sort=sort,
        order=order,
        search=search
    )

    serialized_items = [schemas.CategoryResponse.model_validate(item) for item in items]

    return {
        "items": serialized_items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }


@router.get("/statistics", response_model=dict)
def get_categories_statistics(
        user_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = crud.CategoryCRUD.get_statistics(db, user_id)
    return stats


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(
        user_id: UUID,
        category_id: UUID,
        db: Session = Depends(get_db)
):
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = crud.CategoryCRUD.get_by_id(db, category_id, user_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return schemas.CategoryResponse.model_validate(category)


@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
def create_category(
        user_id: UUID,
        category: schemas.CategoryCreate,
        db: Session = Depends(get_db)
):
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db_category = crud.CategoryCRUD.create(db, category, user_id)
        return schemas.CategoryResponse.model_validate(db_category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create category: {str(e)}")


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
        user_id: UUID,
        category_id: UUID,
        category_update: schemas.CategoryUpdate,
        db: Session = Depends(get_db)
):
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db_category = crud.CategoryCRUD.update(db, category_id, user_id, category_update)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return schemas.CategoryResponse.model_validate(db_category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
def delete_category(
        user_id: UUID,
        category_id: UUID,
        db: Session = Depends(get_db)
):
    # transactions: on delete restrict
    try:
        user = crud.UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        deleted = crud.CategoryCRUD.delete(db, category_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete category: {str(e)}")
    return None