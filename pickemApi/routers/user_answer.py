"""
Routers for managing answers of users APIs.
"""

import logging
import json
from fastapi import Depends, APIRouter, HTTPException
from pickemApi.schemas.events import UserAnswerCreate, UserAnswerResponse
from pickemApi.models.usermanager import current_active_user
from pickemApi.database import AsyncSession, get_db
from pickemApi.models.model import User, UserAnswer
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/answers/", response_model=UserAnswerResponse, status_code=201)
async def submit_answer(
    answer: UserAnswerCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """Submit user's answer to database."""
    user_answer = (
        json.dumps(answer.answer) if isinstance(answer.answer, list) else answer.answer
    )

    existing_answer = await db.execute(
        select(UserAnswer).where(
            UserAnswer.user_id == user.id,
            UserAnswer.event_id == answer.event_id,
        )
    )
    if existing_answer.scalar() is not None:
        # Jeśli odpowiedź już istnieje, zwróć błąd
        logger.warning(
            f"User {user.id} already submitted an answer for event {answer.event_id}."
        )
        raise HTTPException(
            status_code=409,
            detail="You have already submitted an answer for this event.",
        )

    new_answer = UserAnswer(
        user_id=user.id,
        event_id=answer.event_id,
        answer=user_answer,
    )
    logger.info("Adding user's answer to database.")
    db.add(new_answer)
    try:
        await db.commit()
        await db.refresh(new_answer)
        logger.info("Succesfully addes answer to database.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding answer: {e}")

    return new_answer
