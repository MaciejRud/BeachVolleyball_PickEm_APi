"""
Tests for event services.
"""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from pickemApi.services.event_solution_service import set_event_solution_service
from pickemApi.models.model import Event, QuestionType
from pickemApi.schemas.events import EventSolutionCreate
from fastapi import HTTPException


@pytest.mark.anyio
async def test_set_solution_success():
    mock_event = Event(id=uuid4(), question_type=QuestionType.YES_NO)
    mock_db = AsyncMock()
    mock_db.get.return_value = mock_event

    solution_data = EventSolutionCreate(solution="yes")
    result = await set_event_solution_service(
        event_id=mock_event.id, solution_data=solution_data, db=mock_db
    )
    print(result)
    assert result.solution == solution_data.solution
    mock_db.commit.assert_called_once()


@pytest.mark.anyio
async def test_set_solution_invalid_format():
    mock_event = Event(id=1, question_type=QuestionType.SINGLE_CHOICE)
    mock_db = AsyncMock()
    mock_db.get.return_value = mock_event

    solution = EventSolutionCreate(solution=["Team A", "Team B"])
    with pytest.raises(
        HTTPException,
        match="Solution must be a single string for SINGLE_CHOICE questions.",
    ):
        await set_event_solution_service(
            event_id=mock_event.id, solution_data=solution, db=mock_db
        )


@pytest.mark.anyio
async def test_set_solution_event_not_found():
    mock_db = AsyncMock()
    mock_db.get.return_value = None

    solution = "yes"
    with pytest.raises(Exception, match="Event not found"):
        await set_event_solution_service(event_id=1, solution_data=solution, db=mock_db)
