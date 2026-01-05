import pytest

def test_stratified_filter_error():
    from mcqpy.question.filter.stratified import StratifiedFilter
    with pytest.raises(ValueError):
        StratifiedFilter(number_of_questions=10)

def test_stratified_filter_length_mismatch():
    from mcqpy.question.filter import TagFilter
    from mcqpy.question.filter.stratified import StratifiedFilter
    filters = [TagFilter(tags=["math"])]
    with pytest.raises(ValueError):
        StratifiedFilter(filters=filters, proportions=[0.5, 0.5], number_of_questions=10)

def test_stratified_filter_no_proportions():
    from mcqpy.question.filter import TagFilter
    from mcqpy.question.filter.stratified import StratifiedFilter
    filters = [TagFilter(tags=["math"]), TagFilter(tags=["science"])]
    stratified_filter = StratifiedFilter(filters=filters, number_of_questions=10)
    assert stratified_filter.proportions == [0.5, 0.5]

def test_stratified_filter_normalization():
    from mcqpy.question.filter import TagFilter
    from mcqpy.question.filter.stratified import StratifiedFilter
    filters = [TagFilter(tags=["math"]), TagFilter(tags=["science"])]
    stratified_filter = StratifiedFilter(filters=filters, proportions=[1, 3], number_of_questions=10)
    assert stratified_filter.proportions == [0.25, 0.75]

def test_stratified_filter(stratified_filter, question_set_with_meta):
    filtered_questions = stratified_filter.apply(question_set_with_meta)
    math_count = sum(1 for q in filtered_questions if "math" in q.tags)
    science_count = sum(1 for q in filtered_questions if "science" in q.tags)

    assert len(filtered_questions) == 6
    assert math_count == 3
    assert science_count == 3

def test_stratified_filter_configs(stratified_filter_configs, question_set_with_meta):
    filtered_questions = stratified_filter_configs.apply(question_set_with_meta)
    math_count = sum(1 for q in filtered_questions if "math" in q.tags)
    science_count = sum(1 for q in filtered_questions if "science" in q.tags)

    assert len(filtered_questions) == 6
    assert math_count == 3
    assert science_count == 3


