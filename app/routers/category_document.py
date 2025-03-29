from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/categories_document", tags=["categories_document"])


@router.post("/", response_model=schemas.CategoryDocument)
def create_category_document(
    category: schemas.CategoryDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_category = models.CategoryDocument(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=list[schemas.CategoryDocument])
def read_categories_document(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return db.query(models.CategoryDocument).offset(skip).limit(limit).all()


@router.get("/{category_id}", response_model=schemas.CategoryDocument)
def read_category_document(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    category = (
        db.query(models.CategoryDocument)
        .filter(models.CategoryDocument.id == category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="CategoryDocument not found")
    return category


@router.put("/{category_id}", response_model=schemas.CategoryDocument)
def update_category_document(
    category_id: int,
    category: schemas.CategoryDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_category = (
        db.query(models.CategoryDocument)
        .filter(models.CategoryDocument.id == category_id)
        .first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="CategoryDocument not found")

    for key, value in category.dict().items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_category_document(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    category = (
        db.query(models.CategoryDocument)
        .filter(models.CategoryDocument.id == category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="CategoryDocument not found")

    db.delete(category)
    db.commit()
    return {"message": "CategoryDocument deleted successfully"}
