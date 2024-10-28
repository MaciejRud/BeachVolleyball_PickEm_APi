"""
Model for eunm class.
"""

from enum import Enum as Enum_class


class QuestionType(str, Enum_class):
    YES_NO = "yes_no"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
