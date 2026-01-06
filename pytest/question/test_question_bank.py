import pytest
from mcqpy.question import Question, QuestionBank

@pytest.fixture
def question_set(question_factory) -> list[Question]:
    questions = []
    for i in range(10):
        image = i % 3  # 0, 1, or 2 images
        code = (i + 1) % 3  # 0, 1, or 2 code snippets
        question = question_factory(image=image, code=code)
        questions.append(question)
    return questions

@pytest.fixture
def question_directory(tmp_path, question_set):
    dir_path = tmp_path / "questions"
    dir_path.mkdir()

    for i, question in enumerate(question_set):
        file_path = dir_path / f"question_{i + 1}.yaml"
        with open(file_path, "w") as f:
            f.write(question.as_yaml())
    return dir_path

@pytest.fixture
def question_bank(question_directory) -> QuestionBank:
    return QuestionBank.from_directories([question_directory])

def test_question_bank_load(question_bank):
    assert len(question_bank) == 10

def test_question_bank_load_duplicate_slug(question_directory):
    with pytest.raises(ValueError, match="Duplicate slug found"):
        QuestionBank.from_directories([question_directory, question_directory])

def test_get_by_slug(question_bank, question_set):
    for question in question_set:
        fetched_question = question_bank.get_by_slug(question.slug)
        assert fetched_question.slug == question.slug

def test_get_by_slug_not_found(question_bank):
    with pytest.raises(KeyError, match="Slug non_existent_slug not found"):
        question_bank.get_by_slug("non_existent_slug")

def test_get_by_qid(question_bank, question_set):
    for question in question_set:
        fetched_question = question_bank.get_by_qid(question.qid)
        assert fetched_question.qid == question.qid

def test_get_by_qid_not_found(question_bank):
    with pytest.raises(KeyError, match="QID non_existent_qid not found"):
        question_bank.get_by_qid("non_existent_qid")





