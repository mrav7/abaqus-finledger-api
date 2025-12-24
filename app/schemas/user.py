from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"