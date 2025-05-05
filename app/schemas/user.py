from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None 
    username: Optional[str] = None
    password: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: datetime

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "username",
                "id": 1,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }
