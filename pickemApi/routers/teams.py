"""
Routers for managemant of teams.
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pickemApi.database import get_db
from pickemApi.models.usermanager import current_admin_user
from pickemApi.models.model import Team, User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/teams/sample")
async def create_sample_teams(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(current_admin_user)
):
    logger.info("Creating sample teams.")
    sample_teams = [
        Team(id=uuid.uuid4(), player_1=f"Player_{i}_1", player_2=f"Player_{i}_2")
        for i in range(1, 11)
    ]
    db.add_all(sample_teams)
    try:
        await db.commit()
        logger.info("Succesfully added 10 sample teams.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding sample teams: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "10 sample teams added to the database."}
