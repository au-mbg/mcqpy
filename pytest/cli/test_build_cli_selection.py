import pytest
from mcqpy.cli.build import _select_questions
from mcqpy.cli.config import SelectionConfig

@pytest.fixture
def question_bank(question_set):
    from mcqpy.question.question_bank import QuestionBank
    return QuestionBank.from_questions(question_set)

def test_select_questions_default(question_bank):
    config = SelectionConfig()
    selected = _select_questions(question_bank, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_bank.get_all_questions()}
    assert selected_qids == expected_qids

def test_select_questions_noq(question_bank):
    config = SelectionConfig(number_of_questions=None)
    selected = _select_questions(question_bank, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_bank.get_all_questions()}
    assert selected_qids == expected_qids

def test_select_questions_shuffle(question_bank):
    config = SelectionConfig(seed=42, shuffle=True)
    selected = _select_questions(question_bank, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_bank.get_all_questions()}
    assert selected_qids == expected_qids


def test_select_questions_date_no_match(question_bank):
    filters = {"date": {"date_value": "01/10/2023"}}
    config = SelectionConfig(filters=filters)
    selected = _select_questions(question_bank, config)
    assert len(selected) == 0

def test_select_questions_date_all_match(question_bank):
    filters = {"date": {"date_value": "01/01/2024"}}
    config = SelectionConfig(filters=filters)
    selected = _select_questions(question_bank, config)
    assert len(selected) == len(question_bank.get_all_questions())