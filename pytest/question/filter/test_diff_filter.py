import pytest
from mcqpy.question.filter import DifficultyFilter

def test_difficulty_filter(difficulty_filter, question_set_with_meta):
    filtered_questions = difficulty_filter.apply(question_set_with_meta)
    assert all(q.difficulty == difficulty_filter.difficulty for q in filtered_questions)

def test_difficulty_filter_no_diff_attr(difficulty_filter, question_set):
    filtered_questions = difficulty_filter.apply(question_set)
    assert len(filtered_questions) == 0 # None are expected since no difficulty attribute

def test_difficulty_filter_invalid_key(question_set_with_meta):
    with pytest.raises(KeyError):
        diff_filter = DifficultyFilter("invalid_difficulty")
        diff_filter.apply(question_set_with_meta)


def test_composite_tag_difficulty_filter(tag_filter, difficulty_filter, question_set_with_meta):
    composite_filter = tag_filter & difficulty_filter
    filtered_questions = composite_filter.apply(question_set_with_meta)
    for q in filtered_questions:
        if tag_filter.exclude:
            assert 'math' not in q.tags
        else:
            assert 'math' in q.tags
        assert q.difficulty == difficulty_filter.difficulty

