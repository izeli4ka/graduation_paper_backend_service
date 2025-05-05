from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class PosterBase(BaseModel):
    title: str
    content: str  # JSON строка
    template_id: str


class PosterCreate(PosterBase):
    pass


class PosterUpdate(PosterBase):
    title: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[str] = None


class Poster(PosterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    
    class Config:
        orm_mode = True
