from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/types_document", tags=["types_document"])


@router.post("/", response_model=schemas.TypeDocument)
def create_type_document(
    type_doc: schemas.TypeDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_type = models.TypeDocument(**type_doc.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type


@router.get("/", response_model=list[schemas.TypeDocument])
def read_types_document(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return db.query(models.TypeDocument).offset(skip).limit(limit).all()


@router.get("/{type_id}", response_model=schemas.TypeDocument)
def read_type_document(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    type_doc = (
        db.query(models.TypeDocument).filter(models.TypeDocument.id == type_id).first()
    )
    if not type_doc:
        raise HTTPException(status_code=404, detail="TypeDocument not found")
    return type_doc


@router.put("/{type_id}", response_model=schemas.TypeDocument)
def update_type_document(
    type_id: int,
    type_doc: schemas.TypeDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_type = (
        db.query(models.TypeDocument).filter(models.TypeDocument.id == type_id).first()
    )
    if not db_type:
        raise HTTPException(status_code=404, detail="TypeDocument not found")

    for key, value in type_doc.dict().items():
        setattr(db_type, key, value)

    db.commit()
    db.refresh(db_type)
    return db_type


@router.delete("/{type_id}")
def delete_type_document(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    type_doc = (
        db.query(models.TypeDocument).filter(models.TypeDocument.id == type_id).first()
    )
    if not type_doc:
        raise HTTPException(status_code=404, detail="TypeDocument not found")

    db.delete(type_doc)
    db.commit()
    return {"message": "TypeDocument deleted successfully"}
