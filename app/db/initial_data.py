from sqlalchemy.orm import Session
from app.models import Base, User, Role, Organisation
from app.utils.security import get_password_hash
from app.config import settings
from app import models


def create_initial_data(db: Session):
    try:
        admin_role = db.query(models.Role).filter(models.Role.name == "Admin").first()
        if not admin_role:
            admin_role = models.Role(name="Admin", is_active=True)
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        user_role = db.query(models.Role).filter(models.Role.name == "User").first()
        if not user_role:
            user_role = models.Role(name="User", is_active=True)
            db.add(user_role)
            db.commit()

        org = (
            db.query(models.Organisation)
            .filter(models.Organisation.name == "Default Organization")
            .first()
        )
        if not org:
            org = models.Organisation(name="Default Organization", is_active=True)
            db.add(org)
            db.commit()
            db.refresh(org)


        admin = (
            db.query(models.User)
            .filter(models.User.email == settings.FIRST_ADMIN_EMAIL)
            .first()
        )
        if not admin:
            hashed_password = get_password_hash(settings.FIRST_ADMIN_PASSWORD)
            admin = models.User(
                email=settings.FIRST_ADMIN_EMAIL,
                hashed_password=hashed_password,
                full_name=settings.FIRST_ADMIN_FULLNAME,
                is_active=True,
                is_superuser=True,
                role_id=admin_role.id,
                organisation_id=org.id,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        
        reviewer = (
            db.query(models.User)
            .filter(models.User.email == "reviewer@example.com")
            .first()
        )
        if not reviewer:
            reviewer = models.User(
                full_name="Reviewer User",
                email="reviewer@example.com",
                hashed_password=get_password_hash("reviewer_password"),
                is_active=True,
                role_id=user_role.id,
                organisation_id=org.id,
            )
            db.add(reviewer)
            db.commit()
            db.refresh(reviewer)

        doc_type = (
            db.query(models.TypeDocument)
            .filter(models.TypeDocument.name == "Test Type")
            .first()
        )
        if not doc_type:
            doc_type = models.TypeDocument(name="Test Type", is_active=True)
            db.add(doc_type)
            db.commit()
            db.refresh(doc_type)

        doc_category = (
            db.query(models.CategoryDocument)
            .filter(models.CategoryDocument.name == "Test Category")
            .first()
        )
        if not doc_category:
            doc_category = models.CategoryDocument(name="Test Category", is_active=True)
            db.add(doc_category)
            db.commit()
            db.refresh(doc_category)

        doc = (
            db.query(models.Document)
            .filter(models.Document.name == "Initial Document")
            .first()
        )
        if not doc:
            doc = models.Document(
                name="Initial Document",
                type_id=doc_type.id,
                category_id=doc_category.id,
                organisation_id=org.id,
                is_active=True,
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            
            user_doc = (
                db.query(models.UserDocument)
                .filter(
                    models.UserDocument.id_User == admin.id,
                    models.UserDocument.id_Doc == doc.id,
                )
                .first()
            )

            if not user_doc:
                user_doc = models.UserDocument(id_User=admin.id, id_Doc=doc.id)
                db.add(user_doc)
                db.flush()

                user_doc.approvers.append(admin)
                user_doc.reviewers.append(reviewer)

                db.commit()

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Ошибка при инициализации данных: {str(e)}")
