import pytest
from mcqpy_core.grading import GradedSet, StrictRubric, grade_parsed_set
from mcqpy_core.manifest import Manifest
from mcqpy_pdf.parse_pdf import MCQPDFParser
from mcqpy_pdf.utils.fill_form import fill_pdf_form


class PDFPipelineGrader:
    def __init__(
        self, manifest: Manifest, rubric: StrictRubric, regex_pattern: str | None = None
    ):
        self.manifest = manifest
        self.rubric = rubric
        self.regex_pattern = regex_pattern
        self.parser = MCQPDFParser()

    def grade(self, student_answer=None, parsed_set=None) -> GradedSet:
        if parsed_set is None:
            parsed_set = self.parser.parse_pdf(
                student_answer, regex_pattern=self.regex_pattern
            )
        return grade_parsed_set(self.manifest, self.rubric, parsed_set)

@pytest.fixture(scope="module")
def grader(built_mcq) -> PDFPipelineGrader:
    manifest = Manifest.load_from_file(built_mcq.file.with_name(built_mcq.file.stem + "_manifest").with_suffix(".json"))    
    rubric = StrictRubric()
    return PDFPipelineGrader(manifest, rubric)

@pytest.fixture(scope="session")
def filled_pdfs(built_mcq, tmp_path_factory):

    tmp_path = tmp_path_factory.mktemp("filled_pdfs")
    manifest = Manifest.load_from_file(built_mcq.file.with_name(built_mcq.file.stem + "_manifest").with_suffix(".json"))    

    num_filled = 5
    for i in range(num_filled):
        fill_pdf_form(built_mcq.file, tmp_path, index=i, manifest=manifest)

    filled_files = list(tmp_path.glob(f"{built_mcq.file.stem}_autofill_*.pdf"))
    return filled_files


@pytest.fixture(params=[0, 1, 2, 3, 4], scope="module")
def graded_set(request, grader, filled_pdfs) -> GradedSet:
    graded_set = grader.grade(filled_pdfs[request.param])
    return graded_set

@pytest.fixture(scope="module")
def graded_sets(grader, filled_pdfs) -> list[GradedSet]:
    graded_sets = []
    for pdf in filled_pdfs:
        graded_set = grader.grade(pdf)
        graded_sets.append(graded_set)
    return graded_sets
