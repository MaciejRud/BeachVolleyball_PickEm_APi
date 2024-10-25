"""
Routers for managemant of tournaments.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pickemApi.schemas.events import (
    TournamentCreate,
    TournamentResponse,
    EventResponse,
    EventCreate,
    QuestionType,
    TeamResponse,
)
from pickemApi.database import get_db
from pickemApi.models.usermanager import current_admin_user
from pickemApi.models.model import User, Tournament, Team, Event


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


@router.get("/tournaments/{tournament_id}/teams", response_model=list[TeamResponse])
async def get_teams(tournament_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Response all teams of tournament."""
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    list_of_tournament = tournament.teams

    return list_of_tournament


@router.post(
    "/tournaments/{tournament_id}/events", response_model=EventResponse, status_code=201
)
async def create_event(
    tournament_id: uuid.UUID,
    event: EventCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(current_admin_user),
):
    """Creating a new event by admin."""

    # Check if tournament exists
    tournament = await db.get(Tournament, event.tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Check if points_value is >0
    if event.points_value < 0:
        raise HTTPException(status_code=422, detail="Points value must be non-negative")

    # Check if question_type is correct
    if event.question_type not in QuestionType:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question type. Must be one of: {', '.join(q.value for q in QuestionType)}",
        )

    logger.info("Creating new event.")
    new_event = Event(
        tournament_id=tournament_id,
        question_type=event.question_type,
        question_text=event.question_text,
        points_value=event.points_value,
    )
    db.add(new_event)
    try:
        await db.commit()
        await db.refresh(new_event)
        logger.info(f"Succesfully created event: {new_event}")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    return new_event


@router.get("/tournaments/{tournament_id}/events", response_model=list[EventResponse])
async def get_teams(tournament_id: uuid.UUID, db: AsyncSession = Depends(get_db)):  # noqa: F811
    """Response all events of tournament."""
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    list_of_events = tournament.events

    return list_of_events


@router.post("/tournaments/{tournament_id}/finalize")
async def finalize_tournament(
    tournament_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    # Walidacja i obliczanie punktów
    pass
