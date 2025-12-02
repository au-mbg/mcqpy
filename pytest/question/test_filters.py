import pytest
from mcqpy.question.filter import TagFilter, DifficultyFilter, DateFilter
from mcqpy.question import Question

tag_sets = [
    ['math', 'algebra'],
    ['science', 'biology'],
    ['algebra', 'science'],
]

@pytest.fixture
def question_set_with_meta(question_set):
    for index, question in enumerate(question_set):
        tags = tag_sets[index % len(tag_sets)]
        difficulty = 'easy' if index % 3 == 0 else 'hard'
        date_added = f"15/0{index % 9 + 1}/2025"
        dump = question.model_dump()
        dump.update({'tags': tags, 'difficulty': difficulty, 'created_date': date_added})
        new_question = Question.model_validate(dump, context={})
        question_set[index] = new_question        
    return question_set        

@pytest.fixture(params=[True, False])
def tag_filter(request):
    return TagFilter(tags=['math'], exclude=request.param)

@pytest.fixture(params=[True, False])
def tag_match_all_filter(request):
    return TagFilter(tags=['math', 'algebra'], match_all=True, exclude=request.param)


@pytest.fixture(params=['easy', 'hard'])
def difficulty_filter(request):
    return DifficultyFilter(request.param)


@pytest.fixture
def date_filter():
    return DateFilter("01/01/2025")


def test_tag_filter(tag_filter, question_set_with_meta):
    filtered_questions = tag_filter.apply(question_set_with_meta)
    if tag_filter.exclude:
        assert all('math' not in q.tags for q in filtered_questions)
    else:
        assert all('math' in q.tags for q in filtered_questions)

def test_tag_match_all_filter(tag_match_all_filter, question_set_with_meta):
    filtered_questions = tag_match_all_filter.apply(question_set_with_meta)
    if tag_match_all_filter.exclude:
        assert all(not all(tag in q.tags for tag in ['math', 'algebra']) for q in filtered_questions)
    else:
        assert all(all(tag in q.tags for tag in ['math', 'algebra']) for q in filtered_questions)

def test_difficulty_filter(difficulty_filter, question_set_with_meta):
    filtered_questions = difficulty_filter.apply(question_set_with_meta)
    assert all(q.difficulty == difficulty_filter.difficulty for q in filtered_questions)

def test_date_filter(date_filter, question_set_with_meta):
    filtered_questions = date_filter.apply(question_set_with_meta)
    for q in filtered_questions:
        assert q.created_date == "01/01/2025"

def test_composite_tag_difficulty_filter(tag_filter, difficulty_filter, question_set_with_meta):
    composite_filter = tag_filter & difficulty_filter
    filtered_questions = composite_filter.apply(question_set_with_meta)
    for q in filtered_questions:
        if tag_filter.exclude:
            assert 'math' not in q.tags
        else:
            assert 'math' in q.tags
        assert q.difficulty == difficulty_filter.difficulty