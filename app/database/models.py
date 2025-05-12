from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime,  LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    posters = relationship("Poster", back_populates="owner")

class Poster(Base):
    __tablename__ = "posters"
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, index=True)
    content      = Column(Text)              
    html_content = Column(Text, nullable=True)  
    pdf_url      = Column(String, nullable=True) 
    template_id  = Column(String)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id     = Column(Integer, ForeignKey("users.id"))
    owner        = relationship("User", back_populates="posters")
    images = relationship("Image", back_populates="poster")

class Image(Base):
    __tablename__ = "images"
    id        = Column(Integer, primary_key=True, index=True)
    filename  = Column(String, nullable=False)
    url       = Column(String, nullable=True)       # если храним только URL
    data      = Column(LargeBinary, nullable=True)   # или бинарь, но лучше URL
    poster_id = Column(Integer, ForeignKey("posters.id"))
    
    poster    = relationship("Poster", back_populates="images")