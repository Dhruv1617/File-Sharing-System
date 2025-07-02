from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
# from schemas import FileResponse as FileSchema

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FileBase(BaseModel):
    filename: str

class FileResponse(FileBase):
    id: int
    upload_time: datetime
    uploaded_by: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DownloadLink(BaseModel):
    download_link: str
    message: str