"""
Schemas for all functionality in API.
"""

import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
from datetime import date


class QuestionType(str, Enum):
    YES_NO = "yes_no"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


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
    event_id: uuid.UUID
    answer: Union[str, List[str]]


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerResponse(UserAnswerBase):
    id: uuid.UUID
    points: int

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    tournament_id: uuid.UUID
    question_type: QuestionType
    question_text: str
    points_value: int


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: uuid.UUID
    answers: Optional[List[UserAnswerResponse]]

    model_config = ConfigDict(from_attributes=True)
