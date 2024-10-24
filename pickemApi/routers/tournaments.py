"""
Routers for managemant of tournaments.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pickemApi.schemas.events import TournamentCreate, TournamentResponse
from pickemApi.database import get_db
from pickemApi.models.usermanager import current_admin_user
from pickemApi.models.model import User, Tournament


router = APIRouter()


@router.post("/tournaments/", response_model=TournamentResponse, status_code=201)
async def create_tournament(
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_admin_user),
):
    """Creating new tournament by admin."""
    new_tournament = Tournament(name=tournament.name, date=tournament.date)
    db.add(new_tournament)
    try:
        await db.commit()
        await db.refresh(new_tournament)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return new_tournament
