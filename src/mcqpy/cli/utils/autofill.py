"""Compatibility shim for the autofill CLI command now owned by mcqpy-pdf."""

from mcqpy_pdf.cli.utils.autofill import autofill_command

__all__ = ["autofill_command"]
