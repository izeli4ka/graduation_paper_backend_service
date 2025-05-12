from pydantic import BaseModel
from typing import Optional

class ImageBase(BaseModel):
    filename: str
    url: str 

class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: int
    poster_id: int

    class Config:
        orm_mode = True
