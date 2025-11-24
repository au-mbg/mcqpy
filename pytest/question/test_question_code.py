import pytest

@pytest.fixture()
def question_with_code(question_factory):
    question = question_factory(code=True)
    return question

@pytest.fixture()
def question_with_multi_code(question_factory):
    question = question_factory(code=2)
    return question

def test_question_with_code_initialization(question_with_code):
    assert len(question_with_code.code) == 1

def test_code_attribute(question_with_code):
    assert hasattr(question_with_code, "code")

def test_code_language_attribute(question_with_code):
    assert hasattr(question_with_code, "code_language")
    assert question_with_code.code_language == ["python"]

def test_question_with_multi_code_initialization(question_with_multi_code):
    assert len(question_with_multi_code.code) == 2

def test_multi_code_language_attribute(question_with_multi_code):
    assert hasattr(question_with_multi_code, "code_language")
    assert question_with_multi_code.code_language == ["python", "python"]
