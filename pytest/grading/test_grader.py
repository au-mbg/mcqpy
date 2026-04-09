import pytest
from mcqpy_core.grading import GradedSet, ParsedQuestion, ParsedSet, StrictRubric, get_grade_dataframe
from mcqpy_core.manifest import Manifest

@pytest.mark.requires_latex
def test_grader_initialization(grader):
    assert isinstance(grader.manifest, Manifest)
    assert isinstance(grader.rubric, StrictRubric)
    assert grader.parser is not None

@pytest.mark.requires_latex
def test_filled_pdfs_exist(filled_pdfs):
    assert len(filled_pdfs) == 5
    for pdf in filled_pdfs:
        assert pdf.exists()

@pytest.mark.requires_latex
def test_graded_set_type(graded_set):
    assert isinstance(graded_set, GradedSet)

@pytest.mark.requires_latex
def test_graded_set_points(graded_set):
    assert graded_set.max_points > 0
    assert 0 <= graded_set.points <= graded_set.max_points

def test_empty_parsed_set(grader, graded_sets):

    graded_question = graded_sets[0].graded_questions[0]

    sample_question = ParsedQuestion(qid=graded_question.qid, slug=graded_question.slug, answers=[], onehot=[0, 0, 0, 0])
    parsed_set = ParsedSet(student_info={}, questions=[sample_question], file='none.pdf')


    grade_result = grader.grade(parsed_set=parsed_set)

    assert grade_result.state == grade_result.state.SUCCESS
    assert grade_result.other_info is not None
    assert graded_question.qid in grade_result.other_info
    assert "No answers provided" in grade_result.other_info[graded_question.qid]
