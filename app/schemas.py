from pydantic import BaseModel
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool

# Group Schemas
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupResponse(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: str

# Message Schemas
class MessageCreate(BaseModel):
    content: str
    group_id: str

class MessageResponse(BaseModel):
    content: str
    sender_id: str
    group_id: str

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"