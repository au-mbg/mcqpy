from mcqpy.cli.build import _select_questions
from mcqpy.cli.config import SelectionConfig

def test_select_questions_default(question_set):
    config = SelectionConfig()
    selected = _select_questions(question_set, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_set}
    assert selected_qids == expected_qids

def test_select_questions_noq(question_set):
    config = SelectionConfig(number_of_questions=None)
    selected = _select_questions(question_set, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_set}
    assert selected_qids == expected_qids

def test_select_questions_shuffle(question_set):
    config = SelectionConfig(seed=42, shuffle=True)
    selected = _select_questions(question_set, config)
    selected_qids = {q.qid for q in selected}
    expected_qids = {q.qid for q in question_set}
    assert selected_qids == expected_qids


def test_select_questions_date_no_match(question_set):
    filters = {"date": {"date_value": "01/10/2023"}}
    config = SelectionConfig(filters=filters)
    selected = _select_questions(question_set, config)
    assert len(selected) == 0

def test_select_questions_date_all_match(question_set):
    filters = {"date": {"date_value": "01/01/2024"}}
    config = SelectionConfig(filters=filters)
    selected = _select_questions(question_set, config)
    assert len(selected) == len(question_set)
