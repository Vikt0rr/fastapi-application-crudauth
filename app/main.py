from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, models
from app.database import engine, get_db, Base, SessionLocal
from sqlalchemy.orm import Session
from app.routers import (
    post,
    role,
    organisation,
    user,
    type_document,
    category_document,
    document,
    user_document,
)
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.config import settings
from datetime import timedelta
from app.db.initial_data import create_initial_data
from app.utils.security import get_password_hash
from app.schemas import User
from app.models import Base, User, UserDocument

app = FastAPI()


app.include_router(post.router)
app.include_router(role.router)
app.include_router(organisation.router)
app.include_router(user.router)
app.include_router(type_document.router)
app.include_router(category_document.router)
app.include_router(document.router)
app.include_router(user_document.router)


@app.post("/create_first_admin/")
def create_first_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).count() > 0:
        raise HTTPException(status_code=400, detail="Admin user already exists")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        is_superuser=True,
        is_active=True,
        role_id=user.role_id,
        organisation_id=user.organisation_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_initial_data(db)
    except Exception as e:
        print(f"Ошибка при запуске: {str(e)}")
        raise
    finally:
        db.close()
