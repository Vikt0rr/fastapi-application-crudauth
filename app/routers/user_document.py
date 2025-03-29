from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app import schemas, models
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from typing import List
from app.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/user_documents", tags=["user_documents"])


@router.post(
    "/", response_model=schemas.UserDocument, status_code=status.HTTP_201_CREATED
)
def create_user_document(
    ud: schemas.UserDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    try:
        user = db.query(models.User).filter(models.User.id == ud.id_User).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        document = (
            db.query(models.Document).filter(models.Document.id == ud.id_Doc).first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        db_ud = models.UserDocument(id_User=ud.id_User, id_Doc=ud.id_Doc)
        db.add(db_ud)
        db.flush()


        for user_id in ud.approvers:
            approver = db.query(models.User).get(user_id)
            if not approver:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Approver with ID {user_id} not found",
                )
            db_ud.approvers.append(approver)

        for user_id in ud.reviewers:
            reviewer = db.query(models.User).get(user_id)
            if not reviewer:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Reviewer with ID {user_id} not found",
                )
            db_ud.reviewers.append(reviewer)

        db.commit()
        db.refresh(db_ud)
        return get_user_document_with_relations(db, db_ud.id)

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error (possibly duplicate entry)",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/", response_model=List[schemas.UserDocument])
def read_user_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    user_documents = (
        db.query(models.UserDocument)
        .options(
            joinedload(models.UserDocument.user),
            joinedload(models.UserDocument.document),
            joinedload(models.UserDocument.approvers),
            joinedload(models.UserDocument.reviewers),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return user_documents


@router.get("/{ud_id}", response_model=schemas.UserDocument)
def read_user_document(
    ud_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    ud = (
        db.query(models.UserDocument)
        .options(
            joinedload(models.UserDocument.user),
            joinedload(models.UserDocument.document),
            joinedload(models.UserDocument.approvers),
            joinedload(models.UserDocument.reviewers),
        )
        .filter(models.UserDocument.id == ud_id)
        .first()
    )

    if not ud:
        raise HTTPException(status_code=404, detail="UserDocument not found")
    return schemas.UserDocument.from_orm(ud)


@router.put("/{ud_id}", response_model=schemas.UserDocument)
def update_user_document(
    ud_id: int,
    ud: schemas.UserDocumentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    try:
        db_ud = (
            db.query(models.UserDocument)
            .filter(models.UserDocument.id == ud_id)
            .first()
        )
        if not db_ud:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="UserDocument not found"
            )

        db_ud.id_User = ud.id_User
        db_ud.id_Doc = ud.id_Doc
        db_ud.approvers.clear()
        db_ud.reviewers.clear()
        db.flush()

        for user_id in ud.approvers:
            approver = db.query(models.User).get(user_id)
            if not approver:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Approver with ID {user_id} not found",
                )
            db_ud.approvers.append(approver)

        for user_id in ud.reviewers:
            reviewer = db.query(models.User).get(user_id)
            if not reviewer:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Reviewer with ID {user_id} not found",
                )
            db_ud.reviewers.append(reviewer)

        db.commit()
        return get_user_document_with_relations(db, ud_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.delete("/{ud_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_document(
    ud_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_ud = (
        db.query(models.UserDocument).filter(models.UserDocument.id == ud_id).first()
    )
    if not db_ud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="UserDocument not found"
        )

    try:
        db_ud.approvers.clear()
        db_ud.reviewers.clear()
        db.delete(db_ud)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


def get_user_document_with_relations(db: Session, ud_id: int):
    return (
        db.query(models.UserDocument)
        .options(
            joinedload(models.UserDocument.user),
            joinedload(models.UserDocument.document),
            joinedload(models.UserDocument.approvers),
            joinedload(models.UserDocument.reviewers),
        )
        .filter(models.UserDocument.id == ud_id)
        .first()
    )
