from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

user_document_approvers = Table(
    "user_document_approvers",
    Base.metadata,
    Column("user_document_id", Integer, ForeignKey("ud.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

user_document_reviewers = Table(
    "user_document_reviewers",
    Base.metadata,
    Column("user_document_id", Integer, ForeignKey("ud.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="role")


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="organisation")
    documents = relationship("Document", back_populates="organisation")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)  
    position_id = Column(Integer, ForeignKey("posts.id"))  
    email = Column(String)  
    telegram = Column(String)  
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    position_rel = relationship("Post", backref="users")
    role_id = Column(Integer, ForeignKey("roles.id"))  
    organisation_id = Column(Integer, ForeignKey("organisations.id"))  

    role = relationship("Role", back_populates="users")
    organisation = relationship("Organisation", back_populates="users")
    approving_documents = relationship(
        "UserDocument",
        secondary=user_document_approvers,
        back_populates="approvers"
    )
    
    reviewing_documents = relationship(
        "UserDocument",
        secondary=user_document_reviewers,
        back_populates="reviewers"
    )
    

    document_relations = relationship("UserDocument", foreign_keys="[UserDocument.id_User]", back_populates="user")

class TypeDocument(Base):
    __tablename__ = "types_document"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)

    documents = relationship("Document", back_populates="type")


class CategoryDocument(Base):
    __tablename__ = "categories_document"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)

    documents = relationship("Document", back_populates="category")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  
    creation_date = Column(Date)  
    closing_date = Column(Date)  
    file_path = Column(String)  
    is_active = Column(Boolean, default=True)
    related_document_id = Column(Integer, ForeignKey("documents.id"))
    related_document = relationship(
        "Document", remote_side=[id], backref="replaced_documents", post_update=True
    )

    type_id = Column(Integer, ForeignKey("types_document.id"))  
    category_id = Column(Integer, ForeignKey("categories_document.id"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))  

    type = relationship("TypeDocument", back_populates="documents")
    category = relationship("CategoryDocument", back_populates="documents")
    organisation = relationship("Organisation", back_populates="documents")
    user_relations = relationship("UserDocument", back_populates="document")


class UserDocument(Base):
    __tablename__ = "ud"

    id = Column(Integer, primary_key=True)
    id_User = Column(Integer, ForeignKey("users.id"))  
    id_Doc = Column(Integer, ForeignKey("documents.id"))    

    user = relationship(
        "User", foreign_keys=[id_User], back_populates="document_relations"
    )
    document = relationship("Document", back_populates="user_relations")

    approvers = relationship(
        "User",
        secondary=user_document_approvers,
        back_populates="approving_documents",  
    )
    reviewers = relationship(
        "User",
        secondary=user_document_reviewers,
        back_populates="reviewing_documents",  
    )
