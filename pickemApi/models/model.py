"""
Databases models for Api.
"""

import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship, DeclarativeBase

from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    events = relationship("Event", back_populates="user")


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)  # Można zmienić na DateTime

    events = relationship("Event", back_populates="tournament")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    question_type = Column(String)  # 'single', 'pair', 'multiple'
    criteria = Column(String)

    tournament = relationship("Tournament", back_populates="events")
    user = relationship("User", back_populates="events")
    answers = relationship("UserAnswer", back_populates="event")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    answer = Column(String)  # Odpowiedzi użytkownika
    points = Column(Integer, default=0)

    user = relationship("User")
    event = relationship("Event", back_populates="answers")
