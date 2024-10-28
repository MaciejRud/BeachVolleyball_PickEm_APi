"""
Test for answers APIs.
"""

import pytest
import uuid
import json
from httpx import AsyncClient
from pickemApi.models.model import QuestionType, Tournament, Event


async def create_event(
    created_tournament: Tournament,
    db_session,
    question_type: QuestionType = QuestionType.SINGLE_CHOICE,
    question_text: str = "Kto wygra mecz?",
    points_value: int = 10,
) -> Event:
    event_data = {
        "id": uuid.uuid4(),
        "tournament_id": created_tournament.id,
        "question_type": question_type,
        "question_text": question_text,
        "points_value": points_value,
    }

    event = Event(**event_data)

    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    return event


@pytest.mark.anyio
async def test_submit_answer(authorized_client: AsyncClient, created_event: Event):
    """Test for adding users answer."""
    answer_data = {
        "user_id": str(authorized_client.user_id),
        "event_id": str(created_event.id),
        "answer": "Tak",
    }

    response = await authorized_client.post("/answers/", json=answer_data)
    print(response.json())
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["event_id"] == answer_data["event_id"]
    assert response_data["answer"] == answer_data["answer"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "event_data, answer_data",
    [
        (
            {
                "question_type": QuestionType.YES_NO,
                "question_text": "Czy Polska wygra?",
                "points_value": 10,
            },
            {"answer": "Tak"},
        ),
        (
            {
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_text": "Kto wygra?",
                "points_value": 20,
            },
            {"answer": "Brazylia"},
        ),
        (
            {
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "question_text": "Wybierz 2 drużyny",
                "points_value": 15,
            },
            {"answer": ["USA", "Polska"]},
        ),
    ],
)
async def test_submit_answer_for_multiple_events(
    authorized_client: AsyncClient,
    created_tournament: Tournament,
    event_data,
    answer_data,
    db_session,
):
    event = await create_event(
        created_tournament=created_tournament,
        db_session=db_session,
        question_type=event_data["question_type"],
        question_text=event_data["question_text"],
        points_value=event_data["points_value"],
    )
    answer_json = {
        "user_id": str(authorized_client.user_id),
        "event_id": str(event.id),
        **answer_data,
    }
    print(answer_json)

    # Wysyłanie odpowiedzi użytkownika
    response = await authorized_client.post("/answers/", json=answer_json)
    assert response.status_code == 201
    response_data = response.json()
    print(response.json())

    assert response_data["event_id"] == answer_json["event_id"]

    if type(answer_data["answer"]) is list:
        list_of_answers_from_response = json.loads(response_data["answer"])

        for i in range(0, len(list_of_answers_from_response) - 1):
            assert list_of_answers_from_response[i] == answer_json["answer"][i]
    else:
        assert response_data["answer"] == answer_json["answer"]


@pytest.mark.anyio
async def test_submit_duplicate_answer(
    authorized_client: AsyncClient, created_event: Event
):
    answer_data = {
        "user_id": str(authorized_client.user_id),
        "event_id": str(created_event.id),
        "answer": "Tak",
    }
    response = await authorized_client.post("/answers/", json=answer_data)
    assert response.status_code == 201

    response_duplicate = await authorized_client.post("/answers/", json=answer_data)
    assert response_duplicate.status_code == 409
