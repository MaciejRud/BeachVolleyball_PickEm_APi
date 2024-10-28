"""
Routers for managing answers of users APIs.
"""

import uuid

from fastapi import Depends, APIRouter
from pickemApi.core.database import AsyncSession, get_db

router = APIRouter()


@router.post("/events/{event_id}/solution")
async def set_solution(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Walidacja i zapis rozwiązania
    pass
