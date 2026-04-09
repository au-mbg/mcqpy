"""PDF adapters around core grading logic."""

from __future__ import annotations

from pathlib import Path

from mcqpy_core.grading import Rubric, grade_parsed_set
from mcqpy_core.grading.types import GradeState, ParseState, GradeResult
from mcqpy_core.manifest import Manifest

from .parse_pdf import MCQPDFParser


def grade_pdf(
    student_answer: str | Path,
    manifest: Manifest,
    rubric: Rubric,
    regex_pattern: str | None = None,
) -> GradeResult:
    parser = MCQPDFParser()
    parse_result = parser.parse_pdf(student_answer, regex_pattern=regex_pattern)

    if parse_result.state == ParseState.READER_ERROR:
        # If there was an error during parsing, return a graded set with the error message.
        return GradeResult(
            state=GradeState.READER_ERROR,
            error_message=parse_result.error_message,
        )

    grade_result = grade_parsed_set(
        manifest=manifest,
        rubric=rubric,
        parsed_set=parse_result.parsed_set,
    )
    return grade_result
