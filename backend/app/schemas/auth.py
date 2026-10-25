from pydantic import BaseModel, EmailStr, Field
from app.models.user import Role

class FirstRunSetupIn(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    admin_name: str = Field(min_length=2, max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    name: str
    must_change_password: bool

class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

class SetupStatusOut(BaseModel):
    setup_completed: bool