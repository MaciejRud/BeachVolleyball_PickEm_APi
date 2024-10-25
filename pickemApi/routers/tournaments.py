"""
Routers for managemant of tournaments.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pickemApi.schemas.events import TournamentCreate, TournamentResponse, TeamResponse
from pickemApi.database import get_db
from pickemApi.models.usermanager import current_admin_user
from pickemApi.models.model import User, Tournament, Team


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/tournaments/", response_model=TournamentResponse, status_code=201)
async def create_tournament(
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_admin_user),
):
    """Creating new tournament by admin."""
    logger.info("Creating new tournament.")
    new_tournament = Tournament(name=tournament.name, date=tournament.date)
    db.add(new_tournament)
    try:
        await db.commit()
        await db.refresh(new_tournament)
        logger.info(f"Succesfully created tournament: {new_tournament}.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating tournament: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return new_tournament


@router.post("/tournaments/{tournament_id}/teams/add_last")
async def add_last_teams_to_tournament(
    tournament_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_admin_user),
):
    # Fetch the last 10 teams from the database
    try:
        result = await db.execute(select(Team).order_by(Team.id.desc()).limit(10))
        last_teams = result.scalars().all()

        if not last_teams:
            raise HTTPException(
                status_code=404, detail="No teams found in the database."
            )

        tournament = await db.get(Tournament, tournament_id)
        tournament.teams.extend(last_teams)

        await db.commit()
        logger.info(f"Added last 10 teams to tournament {tournament_id}")

    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex

    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding last teams to tournament {tournament_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Last 10 teams added to the tournament."}
