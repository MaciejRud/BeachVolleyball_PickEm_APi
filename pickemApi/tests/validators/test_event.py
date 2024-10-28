"""
Tests for event validators.
"""

import pytest
from pickemApi.validators.event_validators import validate_event_solution_type
from pickemApi.models.model import QuestionType
from pydantic import ValidationError
from fastapi import HTTPException


def test_yes_no_solution_valid():
    solution = "yes"
    assert validate_event_solution_type(solution, QuestionType.YES_NO) == solution


def test_yes_no_solution_invalid():
    solution = "maybe"
    with pytest.raises(
        HTTPException, match="Solution must be 'yes' or 'no' for YES_NO questions."
    ):
        validate_event_solution_type(solution, QuestionType.YES_NO)


def test_single_choice_solution_valid():
    solution = "Team A"
    assert (
        validate_event_solution_type(solution, QuestionType.SINGLE_CHOICE) == solution
    )


def test_single_choice_solution_invalid():
    solution = ["Team A", "Team B"]
    with pytest.raises(
        HTTPException,
        match="Solution must be a single string for SINGLE_CHOICE questions.",
    ):
        validate_event_solution_type(solution, QuestionType.SINGLE_CHOICE)


def test_multiple_choice_solution_valid():
    solution = ["Team A", "Team B"]
    assert (
        validate_event_solution_type(solution, QuestionType.MULTIPLE_CHOICE) == solution
    )


def test_multiple_choice_solution_invalid():
    solution = "Team A"
    with pytest.raises(
        HTTPException,
        match="Solution must be a list of strings for MULTIPLE_CHOICE questions.",
    ):
        validate_event_solution_type(solution, QuestionType.MULTIPLE_CHOICE)
