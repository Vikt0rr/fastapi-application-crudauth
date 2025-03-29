from datetime import date
from typing import Optional, List, ForwardRef
from fastapi import UploadFile
from pydantic import BaseModel, Field


class UserDocumentSimple(BaseModel):
    id: int
    id_User: int
    id_Doc: int

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


# POST
class PostBase(BaseModel):
    name: str
    is_active: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        from_attributes = True


# ROLE
class RoleBase(BaseModel):
    name: str
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True


# ORGANISATION
class OrganisationBase(BaseModel):
    name: str
    is_active: bool = True


class OrganisationCreate(OrganisationBase):
    pass


class Organisation(OrganisationBase):
    id: int

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


class UserDocumentSimple(BaseModel):
    id: int
    id_User: int
    id_Doc: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    full_name: str
    position_id: int
    email: str
    telegram: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role_id: int
    organisation_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    position_id: Optional[int] = None
    email: Optional[str] = None
    telegram: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    organisation_id: Optional[int] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: Optional["Role"] = None
    organisation: Optional["Organisation"] = None
    approved_documents: List[UserDocumentSimple] = []
    to_review_documents: List[UserDocumentSimple] = []

    class Config:
        from_attributes = True


# TYPES DOCUMENT
class TypeDocumentBase(BaseModel):
    name: str
    is_active: bool = True


class TypeDocumentCreate(TypeDocumentBase):
    pass


class TypeDocument(TypeDocumentBase):
    id: int

    class Config:
        from_attributes = True


# CATEGORY DOCUMENT
class CategoryDocumentBase(BaseModel):
    name: str
    is_active: bool = True


class CategoryDocumentCreate(CategoryDocumentBase):
    pass


class CategoryDocument(CategoryDocumentBase):
    id: int

    class Config:
        from_attributes = True


# DOCUMENT
class DocumentBase(BaseModel):
    name: str
    creation_date: Optional[date] = None
    closing_date: Optional[date] = None
    related_document_id: Optional[int] = None
    file_path: Optional[str] = None
    is_active: bool = True
    type_id: int
    category_id: int
    organisation_id: int


class DocumentCreate(DocumentBase):
    file: Optional[UploadFile] = None


class Document(DocumentBase):
    id: int
    type: Optional[TypeDocument] = None
    category: Optional[CategoryDocument] = None
    organisation: Optional[Organisation] = None
    related_document: Optional[DocumentBase] = None

    class Config:
        from_attributes = True


# USER_DOCUMENT
class UserDocumentBase(BaseModel):
    id_User: int
    id_Doc: int
    approvers: List[int] = Field(..., description="Список ID утверждающих")
    reviewers: List[int] = Field(..., description="Список ID рецензентов")


class UserDocumentCreate(UserDocumentBase):
    pass


class UserDocument(UserDocumentBase):
    id: int
    user: Optional[UserSimple] = None
    document: Optional[Document] = None
    approvers: List[UserSimple] = Field(
        ..., description="Список утверждающих пользователей"
    )  # Изменили тип
    reviewers: List[UserSimple] = Field(
        ..., description="Список рецензентов"
    )  # Изменили тип

    class Config:
        from_attributes = True


# TOKEN
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserAuth(BaseModel):
    email: str
    password: str


#FORWARD_REFS
User.update_forward_refs()
Document.update_forward_refs()
UserDocument.update_forward_refs()
UserResponse.update_forward_refs()
