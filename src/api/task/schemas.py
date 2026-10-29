from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskResponseSchema(BaseModel):
    id: UUID
    author_id: UUID
    name: str
    description: Optional[str] = None
    status: Optional[bool] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class TaskFullResponseSchema(TaskResponseSchema):

    model_config = ConfigDict(from_attributes=True)


class CreateTaskSchema(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = Field(None, min_length=3)


class UpdateTaskSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None, min_length=3)
    status: Optional[bool] = Field(None)
