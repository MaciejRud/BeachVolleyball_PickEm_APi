"""
Tests for tournaments APIs.
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.future import select

from pickemApi.models.model import QuestionType, Team, Tournament, Event, UserAnswer


@pytest.mark.anyio
async def test_creating_tournament_with_autorization(
    authorized_superclient: AsyncClient,
):
    """Test for creating tournament with permission."""
    tournament_data = {"name": "Puchar Świata", "date": "2024-10-24"}

    res = await authorized_superclient.post("/tournaments/", json=tournament_data)

    print(res.status_code)
    assert res.status_code == 201


@pytest.mark.anyio
async def test_creating_tournament_without_autorization(
    authorized_client: AsyncClient,
):
    """Test for creating tournament with permission."""
    tournament_data = {"name": "Puchar Świata", "date": "2024-10-24"}

    res = await authorized_client.post("/tournaments/", json=tournament_data)

    assert res.status_code == 403


@pytest.mark.anyio
async def test_add_last_teams_to_tournament(
    authorized_superclient: AsyncClient, created_tournament: Tournament, db_session
):
    """Test for adding sample teams to tournament in development env."""
    await authorized_superclient.post("/teams/sample")
    tournament_id = created_tournament.id
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/teams/add_last"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Last 10 teams added to the tournament."}

    # Sprawdź, czy drużyny zostały dodane do turnieju
    response_tournament = await db_session.get(Tournament, tournament_id)

    await db_session.refresh(created_tournament)
    assert response_tournament.teams == created_tournament.teams
    assert (
        len(response_tournament.teams) == 10
    )  # Upewnij się, że 10 drużyn zostało dodanych


@pytest.mark.anyio
async def test_add_last_teams_to_tournament_no_teams(
    authorized_superclient: AsyncClient,
    created_tournament: Tournament,
):
    tournament_id = created_tournament.id
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/teams/add_last"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No teams found in the database."}


# Test dla endpointu create_sample_teams
@pytest.mark.anyio
async def test_create_sample_teams(authorized_superclient: AsyncClient, db_session):
    response = await authorized_superclient.post("/teams/sample")

    assert response.status_code == 200
    assert response.json() == {"message": "10 sample teams added to the database."}

    # Sprawdź, czy drużyny zostały dodane do bazy danych
    teams = await db_session.execute(select(Team))
    assert (
        len(teams.scalars().all()) == 10
    )  # Upewnij się, że 10 drużyn zostało dodanych


@pytest.mark.anyio
async def test_create_sample_teams_multiple_calls(
    authorized_superclient: AsyncClient, db_session
):
    # Pierwsze wywołanie powinno działać poprawnie
    response1 = await authorized_superclient.post("/teams/sample")
    assert response1.status_code == 200

    # Sprawdzamy, że drużyny zostały dodane
    teams1 = await db_session.execute(select(Team))
    assert len(teams1.scalars().all()) == 10

    # Drugie wywołanie powinno dodać kolejne drużyny
    response2 = await authorized_superclient.post("/teams/sample")
    assert response2.status_code == 200

    # Sprawdzamy, że drużyny zostały dodane
    teams2 = await db_session.execute(select(Team))
    assert len(teams2.scalars().all()) == 20  # Powinno być teraz 20 drużyn


@pytest.mark.anyio
async def test_create_event(authorized_superclient, created_tournament):
    event_data = {
        "tournament_id": str(created_tournament.id),
        "question_type": QuestionType.YES_NO,
        "question_text": "Is this a test?",
        "points_value": 10,
    }

    response = await authorized_superclient.post(
        f"/tournaments/{created_tournament.id}/events", json=event_data
    )

    assert response.status_code == 201
    created_event = response.json()
    assert created_event["question_type"] == event_data["question_type"]
    assert created_event["question_text"] == event_data["question_text"]
    assert created_event["points_value"] == event_data["points_value"]


@pytest.mark.anyio
async def test_create_event_invalid_question_type(
    authorized_superclient, created_tournament
):
    event_data = {
        "tournament_id": str(created_tournament.id),
        "question_type": "invalid_type",
        "question_text": "Is this a test?",
        "points_value": 10,
    }

    response = await authorized_superclient.post(
        f"/tournaments/{created_tournament.id}/events", json=event_data
    )

    assert response.status_code == 422  # HTTP 422 Unprocessable Entity


@pytest.mark.anyio
async def test_create_event_missing_fields(authorized_superclient, created_tournament):
    event_data = {
        "tournament_id": str(created_tournament.id),
        "question_text": "Is this a test?",  # Brak question_type
        "points_value": 10,
    }

    response = await authorized_superclient.post(
        f"/tournaments/{created_tournament.id}/events", json=event_data
    )

    assert response.status_code == 422  # HTTP 422 Unprocessable Entity


@pytest.mark.anyio
async def test_create_event_invalid_points_value(
    authorized_superclient, created_tournament
):
    event_data = {
        "tournament_id": str(created_tournament.id),
        "question_type": QuestionType.YES_NO,
        "question_text": "Is this a test?",
        "points_value": -5,  # Nieprawidłowa wartość punktowa
    }

    response = await authorized_superclient.post(
        f"/tournaments/{created_tournament.id}/events", json=event_data
    )

    assert response.status_code == 422  # HTTP 422 Unprocessable Entity


@pytest.mark.anyio
async def test_set_solution_success(authorized_superclient, created_event):
    solution_data = {"solution": "yes"}
    response = await authorized_superclient.post(
        f"/events/{created_event.id}/solution", json=solution_data
    )
    assert response.status_code == 201
    print(response.json())
    assert response.json()["solution"] == solution_data["solution"]


@pytest.mark.anyio
async def test_set_solution_invalid_format(authorized_superclient, created_event):
    solution_data = {"solution": ["yes", "no"]}
    response = await authorized_superclient.post(
        f"/events/{created_event.id}/solution", json=solution_data
    )
    assert response.status_code == 422
    assert (
        "Solution must be a single string for SINGLE_CHOICE questions."
        in response.json()["detail"]
    )


@pytest.mark.anyio
async def test_set_solution_event_not_found(authorized_superclient):
    solution_data = {"solution": "yes"}
    fake_event_id = uuid.uuid4()
    response = await authorized_superclient.post(
        f"/events/{fake_event_id}/solution", json=solution_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


@pytest.mark.anyio
async def test_set_solution_unauthorized_user(authorized_client, created_event):
    solution_data = {"solution": "yes"}
    response = await authorized_client.post(
        f"/events/{created_event.id}/solution", json=solution_data
    )
    assert response.status_code == 403


# Assume that the endpoint is part of the FastAPI app
@pytest.mark.anyio
async def test_finalize_tournament_success(
    authorized_superclient: AsyncClient, db_session
):
    # Setup
    tournament_id = uuid.uuid4()

    # Create events
    event1 = Event(
        tournament_id=tournament_id,
        question_type="YES_NO",
        question_text="Is it sunny?",
        solution="yes",
        points_value=10,
    )
    event2 = Event(
        tournament_id=tournament_id,
        question_type="SINGLE_CHOICE",
        question_text="Choose a team",
        solution="Team A",
        points_value=20,
    )

    db_session.add_all([event1, event2])
    await db_session.commit()

    # Create user and answers
    user_id = uuid.uuid4()
    user_answer1 = UserAnswer(user_id=user_id, event_id=event1.id, answer="yes")
    user_answer2 = UserAnswer(user_id=user_id, event_id=event2.id, answer="Team A")

    db_session.add_all([user_answer1, user_answer2])
    await db_session.commit()

    # Call the endpoint
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/finalize"
    )

    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["tournament_id"] == str(tournament_id)
    assert len(result["ranking"]) == 1
    assert result["ranking"]["1"]["user_id"] == str(user_id)
    assert result["ranking"]["1"]["points"] == 30  # All points awarded to the user


@pytest.mark.anyio
async def test_finalize_tournament_multiple_users(
    authorized_superclient: AsyncClient, db_session
):
    # Setup
    tournament_id = uuid.uuid4()

    # Create events
    event = Event(
        tournament_id=tournament_id,
        question_type="YES_NO",
        question_text="Is it sunny?",
        solution="yes",
        points_value=10,
    )

    db_session.add(event)
    await db_session.commit()

    # Create users and answers
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    user_answer1 = UserAnswer(user_id=user1_id, event_id=event.id, answer="yes")
    user_answer2 = UserAnswer(user_id=user2_id, event_id=event.id, answer="no")

    db_session.add_all([user_answer1, user_answer2])
    await db_session.commit()

    # Call the endpoint
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/finalize"
    )

    # Check response
    assert response.status_code == 200
    result = response.json()
    assert len(result["ranking"]) == 1
    assert result["ranking"]["1"]["user_id"] == str(user1_id)
    assert result["ranking"]["1"]["points"] == 10  # Only user1 gets points


@pytest.mark.anyio
async def test_finalize_tournament_incorrect_answers(
    authorized_superclient: AsyncClient, db_session
):
    # Setup
    tournament_id = uuid.uuid4()

    # Create events
    event = Event(
        tournament_id=tournament_id,
        question_type="YES_NO",
        question_text="Is it sunny?",
        solution="yes",
        points_value=10,
    )

    db_session.add(event)
    await db_session.commit()

    # Create user and incorrect answer
    user_id = uuid.uuid4()
    user_answer = UserAnswer(user_id=user_id, event_id=event.id, answer="no")

    db_session.add(user_answer)
    await db_session.commit()

    # Call the endpoint
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/finalize"
    )

    # Check response
    assert response.status_code == 200
    result = response.json()
    assert len(result["ranking"]) == 0  # No ranking since the answer was incorrect


@pytest.mark.anyio
async def test_finalize_tournament_no_events(
    authorized_superclient: AsyncClient, db_session
):
    # Setup
    tournament_id = uuid.uuid4()

    # Call the endpoint without adding any events
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/finalize"
    )

    # Check for 404 error
    assert response.status_code == 404
    assert response.json()["detail"] == "No events found for this tournament"


@pytest.mark.anyio
async def test_finalize_tournament_no_answers(
    authorized_superclient: AsyncClient, db_session
):
    # Setup
    tournament_id = uuid.uuid4()

    # Create events but no answers
    event = Event(
        tournament_id=tournament_id,
        question_type="YES_NO",
        question_text="Is it sunny?",
        solution="yes",
        points_value=10,
    )

    db_session.add(event)
    await db_session.commit()

    # Call the endpoint
    response = await authorized_superclient.post(
        f"/tournaments/{tournament_id}/finalize"
    )

    # Check response
    assert response.status_code == 200
    result = response.json()
    assert len(result["ranking"]) == 0  # No ranking as no answers are provided
