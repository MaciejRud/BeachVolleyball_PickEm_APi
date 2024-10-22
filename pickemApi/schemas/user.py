"""
Schemas for user models.
"""

import uuid

from fastapi_users import schemas


class UserIn(schemas.BaseUserCreate):
    """Schema for creating user."""

    username: str


class UserResponse(schemas.BaseUser[uuid.UUID]):
    """Schema for user response."""

    username: str

    class Config:
        from_attributes = True
