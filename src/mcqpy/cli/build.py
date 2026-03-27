"""Compatibility shims for the build CLI command now owned by mcqpy-pdf."""

from mcqpy.cli._selection import _build_filter, build_filters, select_questions
from mcqpy_pdf.cli.build import build_command


_select_questions = select_questions

__all__ = [
    "build_command",
    "select_questions",
    "_select_questions",
    "_build_filter",
    "build_filters",
]
