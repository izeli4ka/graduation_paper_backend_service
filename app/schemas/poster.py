from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.image import ImageResponse

class PosterBase(BaseModel):
    title: str
    content: str
    template_id: str
    html_content: Optional[str] = None

class PosterCreate(PosterBase):
    pass

class PosterUpdate(BaseModel):
    title:        Optional[str] = Field(default=None)
    content:      Optional[str] = Field(default=None)
    template_id:  Optional[str] = Field(default=None)
    html_content: Optional[str] = Field(default=None)
    
    model_config = ConfigDict(from_attributes=True)

    

class PosterResponse(PosterBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[ImageResponse] = []  

    class Config:
        orm_mode = True
