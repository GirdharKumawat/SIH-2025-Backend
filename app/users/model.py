from pydantic import BaseModel, EmailStr

# User signup schema
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

# User login schema
class UserLogin(BaseModel):
    username: str
    password: str
