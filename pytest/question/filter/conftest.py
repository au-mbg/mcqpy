import pytest
from mcqpy.question import Question
from mcqpy.question.filter import TagFilter, DifficultyFilter, DateFilter

tag_sets = [
    ["math", "algebra"],
    ["science", "biology"],
    ["algebra", "science"],
]


@pytest.fixture
def question_set_with_meta(question_set):
    for index, question in enumerate(question_set):
        tags = tag_sets[index % len(tag_sets)]
        difficulty = "easy" if index % 3 == 0 else "hard"
        date_added = f"15/0{index % 9 + 1}/2025"
        dump = question.model_dump()
        dump.update(
            {"tags": tags, "difficulty": difficulty, "created_date": date_added}
        )
        new_question = Question.model_validate(dump, context={})
        question_set[index] = new_question
    return question_set


@pytest.fixture(params=[True, False])
def tag_filter(request):
    return TagFilter(tags=["math"], exclude=request.param)


@pytest.fixture(params=[True, False])
def tag_match_all_filter(request):
    return TagFilter(tags=["math", "algebra"], match_all=True, exclude=request.param)


@pytest.fixture(params=["easy", "hard"])
def difficulty_filter(request):
    return DifficultyFilter(request.param)


@pytest.fixture
def date_filter():
    return DateFilter("01/01/2025")
