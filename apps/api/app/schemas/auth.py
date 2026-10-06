from pydantic import BaseModel, EmailStr


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    authenticated: bool = False
    message: str = "Authentication is not configured yet."
