from io import BytesIO
import pytest
from mcqpy.question import Question


@pytest.fixture()
def basic_question():
    question = Question(
        slug="sample-question",
        text="What is the capital of France?",
        choices=["Berlin", "Madrid", "Paris", "Rome"],
        correct_answers=[2],
        question_type="single",
    )
    return question


def test_question_initialization(basic_question):
    assert basic_question.slug == "sample-question"
    assert basic_question.text == "What is the capital of France?"
    assert basic_question.choices == ["Berlin", "Madrid", "Paris", "Rome"]
    assert basic_question.correct_answers == [2]
    assert basic_question.question_type == "single"

def test_has_qid(basic_question):
    assert hasattr(basic_question, "qid")
    assert isinstance(basic_question.qid, str)
    assert len(basic_question.qid) > 0

def test_has_point_vale(basic_question):
    assert hasattr(basic_question, "point_value")
    assert isinstance(basic_question.point_value, int)
    assert basic_question.point_value == 1  # Default point value

def test_has_permutation(basic_question):
    assert hasattr(basic_question, "permutation")
    assert isinstance(basic_question.permutation, list)
    assert basic_question.permutation == [i for i in range(len(basic_question.choices))]  # Default permutation

def test_yaml_serialization(basic_question):
    yaml = basic_question.as_yaml()
    assert isinstance(yaml, str)
    assert "sample-question" in yaml
    assert "What is the capital of France?" in yaml
    assert "Berlin" in yaml
    assert "Madrid" in yaml
    assert "Paris" in yaml
    assert "Rome" in yaml

def test_yaml_roundtrip(basic_question, tmp_path):


    yaml = basic_question.as_yaml()
    yaml_file = tmp_path / "question.yaml"
    with open(yaml_file, "w") as f:
        f.write(yaml)

    new_question = Question.load_yaml(yaml_file)
    assert new_question.slug == basic_question.slug
    assert new_question.text == basic_question.text
    assert new_question.choices == basic_question.choices
    assert new_question.correct_answers == basic_question.correct_answers
    assert new_question.question_type == basic_question.question_type

