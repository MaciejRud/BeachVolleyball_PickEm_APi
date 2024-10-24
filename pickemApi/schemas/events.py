"""
Schemas for all functionality in API.
"""

import uuid
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date


class TeamBase(BaseModel):
    player_1: str
    player_2: str


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class TournamentBase(BaseModel):
    name: str
    date: date


class TournamentCreate(TournamentBase):
    pass


class TournamentResponse(TournamentBase):
    id: uuid.UUID
    teams: Optional[List[TeamResponse]]

    model_config = ConfigDict(from_attributes=True)


class UserAnswerBase(BaseModel):
    user_id: uuid.UUID
    answer: str


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerResponse(UserAnswerBase):
    id: uuid.UUID
    points: int

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    tournament_id: uuid.UUID
    question_type: str
    question_text: str
    points_value: int


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: uuid.UUID
    answers: List[UserAnswerResponse]

    model_config = ConfigDict(from_attributes=True)
