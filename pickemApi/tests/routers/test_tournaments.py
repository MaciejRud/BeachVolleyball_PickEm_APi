"""
Tests for tournaments APIs.
"""

import pytest
from httpx import AsyncClient


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
