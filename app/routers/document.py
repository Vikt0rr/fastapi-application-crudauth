from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import date
from app.models import Document as DBDocument 
from app.schemas import Document, DocumentCreate, DocumentBase, User 
from app.database import get_db
import uuid
from app.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIRECTORY = "uploads/documents"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/", response_model=Document)
async def create_document(
    document_data: DocumentCreate = Depends(),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    file_path = None
    if file:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    

    db_document = DBDocument(
        name=document_data.name,
        creation_date=document_data.creation_date,
        closing_date=document_data.closing_date,
        related_document_id=document_data.related_document_id,
        file_path=file_path,
        is_active=document_data.is_active,
        type_id=document_data.type_id,
        category_id=document_data.category_id,
        organisation_id=document_data.organisation_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.get("/", response_model=List[Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    type_id: int = None,
    category_id: int = None,
    organisation_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(DBDocument)

    if is_active is not None:
        query = query.filter(DBDocument.is_active == is_active)
    if type_id:
        query = query.filter(DBDocument.type_id == type_id)
    if category_id:
        query = query.filter(DBDocument.category_id == category_id)
    if organisation_id:
        query = query.filter(DBDocument.organisation_id == organisation_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{document_id}", response_model=Document)
def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_document = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: int,
    document_data: DocumentCreate = Depends(),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    db_document = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = db_document.file_path
    if file:
        # Delete old file if exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

 
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)


        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())


    for field, value in document_data.dict(exclude_unset=True).items():
        if field != "file":  # Skip the file field from the form data
            setattr(db_document, field, value)

    db_document.file_path = file_path
    db.commit()
    db.refresh(db_document)

    return db_document


@router.patch("/{document_id}", response_model=Document)
def partial_update_document(
    document_id: int,
    document_data: DocumentBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    db_document = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    for field, value in document_data.dict(exclude_unset=True).items():
        setattr(db_document, field, value)

    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/{document_id}", response_model=Document)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):

    db_document = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    db_document.is_active = False
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/{document_id}/file")
async def download_document_file(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    db_document = db.query(DBDocument).filter(DBDocument.id == document_id).first()
    if not db_document or not db_document.file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(db_document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(db_document.file_path, filename=os.path.basename(db_document.file_path))
