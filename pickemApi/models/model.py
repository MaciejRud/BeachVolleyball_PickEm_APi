"""
Databases models for Api.
"""

import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    UUID,
    Date,
    Table,
)
from sqlalchemy.orm import relationship, DeclarativeBase

from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Base(DeclarativeBase):
    pass


# Join table that establishes a many-to-many relationship (tournament-teams)
tournament_teams = Table(
    "tournament_teams",
    Base.metadata,
    Column("tournament_id", ForeignKey("tournaments.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    answers = relationship("UserAnswer", back_populates="user", lazy="selectin")


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, index=True)
    date = Column(Date, index=True)

    teams = relationship(
        "Team",
        secondary=tournament_teams,
        back_populates="tournaments",
        lazy="selectin",
    )

    events = relationship("Event", back_populates="tournament", lazy="selectin")


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    player_1 = Column(String, nullable=False)
    player_2 = Column(String, nullable=False)

    tournaments = relationship(
        "Tournament",
        secondary=tournament_teams,
        back_populates="teams",
        lazy="selectin",
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    tournament_id = Column(UUID, ForeignKey("tournaments.id"))
    question_type = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    solution = Column(String, nullable=True)
    points_value = Column(Integer, nullable=False)

    tournament = relationship("Tournament", back_populates="events", lazy="selectin")
    answers = relationship("UserAnswer", back_populates="event", lazy="selectin")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    event_id = Column(UUID, ForeignKey("events.id"))
    answer = Column(String, nullable=False)
    points = Column(Integer, default=0)

    user = relationship("User", back_populates="answers", lazy="selectin")
    event = relationship("Event", back_populates="answers", lazy="selectin")
