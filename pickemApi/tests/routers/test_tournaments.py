"""
Tests for tournaments APIs.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from pickemApi.models.model import Team, Tournament


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
