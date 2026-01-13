import pytest
from mcqpy.grade.parse_pdf import MCQPDFParser

@pytest.fixture(scope="module")
def parser():
    return MCQPDFParser()

@pytest.mark.parametrize(["filename", "expected"], [
    ("mcq_12345_67890.pdf", {"id1": 12345, "id2": 67890}),
    ("mcq_abcde_fghij.pdf", {"id1": "abcde", "id2": "fghij"}),
    ("mcq_001_002.pdf", {"id1": 1, "id2": 2}),
])
def test_find_student_info_regex(parser, filename, expected):
    regex_pattern = "mcq_(?P<id1>\w+)_(?P<id2>\w+).pdf"
    result = parser._find_student_info(fields={}, filename=filename, regex_pattern=regex_pattern)
    assert result == expected




