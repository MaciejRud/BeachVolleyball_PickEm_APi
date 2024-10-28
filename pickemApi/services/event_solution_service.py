"""
The business logic for an event.
"""

import uuid
import logging
import json
from fastapi import HTTPException
from pickemApi.models.model import Event
from pickemApi.schemas.events import EventSolutionCreate
from pickemApi.validators.event_validators import validate_event_solution_type
from pickemApi.core.database import AsyncSession

logger = logging.getLogger(__name__)


async def set_event_solution_service(
    event_id: uuid.UUID,
    solution_data: EventSolutionCreate,
    db: AsyncSession,
):
    logger.info("Setting event solution.")
    # Fetch the event to ensure it exists
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Validate solution type
    validate_event_solution_type(solution_data.solution, event.question_type)

    # Store solution as JSON if it's a list, otherwise as a string
    solution = (
        json.dumps(solution_data.solution)
        if isinstance(solution_data.solution, list)
        else solution_data.solution
    )
    print(solution)

    # Update the solution field in the Event model
    event.solution = solution  # Assume 'solution' is a field on the Event model

    print(event.solution)
    try:
        await db.commit()
        await db.refresh(event)
        logger.info(f"Successfully set solution for event: {event.id}")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error setting solution for event: {e}")
        raise HTTPException(status_code=400, detail="Could not set event solution")

    return event
