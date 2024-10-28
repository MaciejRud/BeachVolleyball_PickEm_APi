"""
Logic for checking answers with solutions.
"""

from pickemApi.models.enums import QuestionType
from typing import Union, List


def check_answer(
    answer: Union[str, List[str]],
    solution: Union[str, List[str]],
    question_type: QuestionType,
) -> bool:
    """Check answers with solution according to type of question."""
    if question_type == QuestionType.YES_NO:
        return answer.lower() == solution.lower()
    elif question_type == QuestionType.SINGLE_CHOICE:
        return (
            answer == solution
        )  # or implement custom comparison logic for objects in the future
    elif question_type == QuestionType.MULTIPLE_CHOICE:
        if isinstance(answer, list) and isinstance(solution, list):
            return sorted(answer) == sorted(solution)  # Order doesn't matter
    return False
