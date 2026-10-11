from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import APIModel


class SignInRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=1024)


class RegisterRequest(SignInRequest):
    pass


class EmailActionRequest(BaseModel):
    email: EmailStr


class TokenActionRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class PasswordResetRequest(TokenActionRequest):
    password: str = Field(min_length=12, max_length=1024)


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=12, max_length=1024)


class UserRead(APIModel):
    id: str
    email: EmailStr
    is_admin: bool = False


class RegistrationResponse(APIModel):
    id: str
    email: EmailStr
    verification_required: bool
    message: str


class ActionResponse(APIModel):
    message: str
