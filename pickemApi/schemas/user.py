"""
Schemas for user models.
"""

import uuid
from pydantic import ConfigDict
from fastapi_users import schemas


class UserIn(schemas.BaseUserCreate):
    """Schema for creating user."""

    username: str


class UserSuperIn(UserIn):
    is_superuser: bool


class UserResponse(schemas.BaseUser[uuid.UUID]):
    """Schema for user response."""

    username: str

    model_config = ConfigDict(from_attributes=True)
