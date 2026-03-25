"""PDF adapters around core grading logic."""

from __future__ import annotations

from pathlib import Path

from mcqpy_core.grading import Rubric, grade_parsed_set
from mcqpy_core.manifest import Manifest

from .parse_pdf import MCQPDFParser


def grade_pdf(
    student_answer: str | Path,
    manifest: Manifest,
    rubric: Rubric,
    regex_pattern: str | None = None,
):
    parser = MCQPDFParser()
    parsed_set = parser.parse_pdf(student_answer, regex_pattern=regex_pattern)
    return grade_parsed_set(manifest=manifest, rubric=rubric, parsed_set=parsed_set)
