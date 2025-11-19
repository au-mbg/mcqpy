import pytest

from mcqpy.question import Question


def test_question_creation():
    question = Question(
        slug="sample-question",
        text="What is the capital of France?",
        choices=["Berlin", "Madrid", "Paris", "Rome"],
        correct_answers=[2],
        question_type="single",
    )
