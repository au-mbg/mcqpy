import pytest
from mcqpy.question import Question

@pytest.fixture()
def question_with_code():
    question = Question(
        slug="code-question",
        text="What does the following code output?",
        choices=["3", "4", "5", "22"],
        code="print(2 + 2)",
        code_language="python",
        correct_answers=[1],
        question_type="single",
    )
    return question

@pytest.fixture()
def question_with_multi_code():
    question = Question(
        slug="multi-code-question",
        text="What are the outputs of the following code snippets?",
        choices=["3", "4", "5", "22"],
        code=["print(2 + 2)", "print(3 + 2)"],
        code_language=["python", "python"],
        correct_answers=[1, 2],
        question_type="multiple",
    )
    return question

def test_question_with_code_initialization(question_with_code):
    assert question_with_code.slug == "code-question"

def test_code_attribute(question_with_code):
    assert hasattr(question_with_code, "code")
    assert question_with_code.code[0] == "print(2 + 2)"

def test_code_language_attribute(question_with_code):
    assert hasattr(question_with_code, "code_language")
    assert question_with_code.code_language[0] == "python"

def test_question_with_multi_code_initialization(question_with_multi_code):
    assert question_with_multi_code.slug == "multi-code-question"

def test_multi_code_attribute(question_with_multi_code):
    assert hasattr(question_with_multi_code, "code")
    assert question_with_multi_code.code == ["print(2 + 2)", "print(3 + 2)"]

def test_multi_code_language_attribute(question_with_multi_code):
    assert hasattr(question_with_multi_code, "code_language")
    assert question_with_multi_code.code_language == ["python", "python"]
