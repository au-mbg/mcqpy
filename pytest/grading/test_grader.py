import pytest
from mcqpy.grade import MCQGrader
from mcqpy.grade.utils import GradedSet
from mcqpy.compile.manifest import Manifest
from mcqpy.grade.rubric import StrictRubric
from mcqpy.utils.fill_form import fill_pdf_form

@pytest.fixture(scope="module")
def grader(built_mcq) -> MCQGrader:
    manifest = Manifest.load_from_file(built_mcq.file.with_name(built_mcq.file.stem + "_manifest").with_suffix(".json"))    
    rubric = StrictRubric()
    return MCQGrader(manifest, rubric)

@pytest.fixture(scope="module")
def filled_pdfs(built_mcq, tmp_path_factory):

    tmp_path = tmp_path_factory.mktemp("filled_pdfs")
    manifest = Manifest.load_from_file(built_mcq.file.with_name(built_mcq.file.stem + "_manifest").with_suffix(".json"))    

    num_filled = 5
    for i in range(num_filled):
        fill_pdf_form(built_mcq.file, tmp_path, index=i, manifest=manifest)

    filled_files = list(tmp_path.glob(f"{built_mcq.file.stem}_autofill_*.pdf"))
    return filled_files

@pytest.mark.requires_latex
@pytest.fixture(params=[0, 1, 2, 3, 4], scope="module")
def graded_set(request, grader, filled_pdfs) -> GradedSet:
    graded_set = grader.grade(filled_pdfs[request.param])
    return graded_set

@pytest.mark.requires_latex
def test_grader_initialization(grader):
    assert isinstance(grader, MCQGrader)
    assert isinstance(grader.manifest, Manifest)
    assert isinstance(grader.rubric, StrictRubric)

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










