"""
Logic of tournament API.
"""

import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pickemApi.models.model import Event, UserAnswer, User
from pickemApi.validators.answer_check import check_answer
from fastapi import HTTPException


logger = logging.getLogger(__name__)


async def finalize_tournament(tournament_id: uuid.UUID, db: AsyncSession):
    try:
        # Fetch all events for the tournament
        tournament_events = await db.execute(
            select(Event).where(Event.tournament_id == tournament_id)
        )
        events = tournament_events.scalars().all()

        if not events:
            raise HTTPException(
                status_code=404, detail="No events found for this tournament"
            )

        # Fetch all user answers for the events
        user_answers = await db.execute(
            select(UserAnswer).where(
                UserAnswer.event_id.in_([event.id for event in events])
            )
        )
        answers = user_answers.scalars().all()

        # Create a dictionary to hold user points
        user_points = {}

        for answer in answers:
            event = next((e for e in events if e.id == answer.event_id), None)
            if event:
                if check_answer(answer.answer, event.solution, event.question_type):
                    # Add points for the user
                    user_points[answer.user_id] = (
                        user_points.get(answer.user_id, 0) + event.points_value
                    )
                    answer.points = event.points_value  # Update points in user answer

        # Update user points in the User table
        for user_id, points in user_points.items():
            user = await db.get(User, user_id)
            if user:
                user.points += points  # Accumulate points for the user

        # Commit all changes
        await db.commit()

        # Prepare the ranking
        ranking = {
            str(rank): {"user_id": user_id, "points": points}
            for rank, (user_id, points) in enumerate(
                sorted(user_points.items(), key=lambda item: item[1], reverse=True),
                start=1,
            )
        }

        return {
            "tournament_id": tournament_id,
            "ranking": ranking,
        }

    except HTTPException as e:
        # Log the HTTPException and re-raise it without converting to 500
        logger.error(f"Error finalizing tournament {tournament_id}: {e.detail}")
        raise

    except Exception as e:
        # Catch other exceptions as 500 errors
        logger.error(f"Unexpected error finalizing tournament {tournament_id}: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while finalizing the tournament"
        )
