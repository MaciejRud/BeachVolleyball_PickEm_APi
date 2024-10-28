"""
Routers for managing answers of users APIs.
"""

import uuid

from fastapi import Depends, APIRouter
from pickemApi.core.database import AsyncSession, get_db
from pickemApi.schemas.events import EventSolutionCreate, EventResponse
from pickemApi.models.usermanager import current_admin_user
from pickemApi.models.model import User
from pickemApi.services.event_solution_service import set_event_solution_service

router = APIRouter()


@router.post(
    "/events/{event_id}/solution", response_model=EventResponse, status_code=201
)
async def set_solution(
    event_id: uuid.UUID,
    solution_data: EventSolutionCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(current_admin_user),
):
    """Sets the correct solution for a specific event by an admin."""
    event = await set_event_solution_service(event_id, solution_data, db)
    return event
