"""Compatibility shim for the grade CLI command now owned by mcqpy-pdf."""

from mcqpy_pdf.cli.grade import grade_command

__all__ = ["grade_command"]
