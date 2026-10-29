from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class RequestUserSchema(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr = Field(min_length=8)
    password: str = Field(min_length=8)
    confirm_password: str = Field(None, min_length=3)

    @field_validator("name", "email")
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value


class ResponseUserSchema(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime


class ResponseUsersListSchema(ResponseUserSchema):

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "id": "b59130db-1223-46b0-8e67-6430476b05c3",
                    "name": "John Doe",
                    "email": "john_doe@example.com",
                    "created_at": "2025-01-01 15:00:00",
                    "deleted": False,
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class EmailRequest(BaseModel):
    email: EmailStr = Field(min_length=8)


class LoginSchema(EmailRequest):
    password: str = Field(min_length=8)

    @field_validator("email", "password")
    def strip_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
