"""
Validation logic for event API.
"""

from pickemApi.models.enums import QuestionType
from fastapi import HTTPException


def validate_event_solution_type(solution, question_type):
    if question_type == QuestionType.YES_NO and solution not in ["yes", "no"]:
        raise HTTPException(
            status_code=422,
            detail="Solution must be 'yes' or 'no' for YES_NO questions.",
        )
    if question_type == QuestionType.SINGLE_CHOICE and not isinstance(solution, str):
        raise HTTPException(
            status_code=422,
            detail="Solution must be a single string for SINGLE_CHOICE questions.",
        )
    if question_type == QuestionType.MULTIPLE_CHOICE:
        if not isinstance(solution, list) or not all(
            isinstance(ans, str) for ans in solution
        ):
            raise HTTPException(
                status_code=422,
                detail="Solution must be a list of strings for MULTIPLE_CHOICE questions.",
            )

    return solution
