from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("/", response_model=schemas.Organisation)
def create_organisation(
    organisation: schemas.OrganisationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_org = models.Organisation(**organisation.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


@router.get("/", response_model=list[schemas.Organisation])
def read_organisations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return db.query(models.Organisation).offset(skip).limit(limit).all()


@router.get("/{org_id}", response_model=schemas.Organisation)
def read_organisation(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    org = db.query(models.Organisation).filter(models.Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org


@router.put("/{org_id}", response_model=schemas.Organisation)
def update_organisation(
    org_id: int,
    org: schemas.OrganisationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    db_org = (
        db.query(models.Organisation).filter(models.Organisation.id == org_id).first()
    )
    if not db_org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    for key, value in org.dict().items():
        setattr(db_org, key, value)

    db.commit()
    db.refresh(db_org)
    return db_org


@router.delete("/{org_id}")
def delete_organisation(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user),
):
    org = db.query(models.Organisation).filter(models.Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    db.delete(org)
    db.commit()
    return {"message": "Organisation deleted successfully"}
