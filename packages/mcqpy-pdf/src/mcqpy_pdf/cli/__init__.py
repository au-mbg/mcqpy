"""Command registration for mcqpy-pdf."""

from mcqpy_pdf.cli.main import main
from mcqpy_pdf.cli.build import build_command
from mcqpy_pdf.cli.check_latex import check_latex_command
from mcqpy_pdf.cli.grade import grade_command
from mcqpy_pdf.cli.utils.autofill import autofill_command
from mcqpy_pdf.cli.utils.main import utils_group


def register_pdf_commands(parent) -> None:
    for name, command in main.commands.items():
        parent.add_command(command, name)


__all__ = [
    "register_pdf_commands",
    "main",
    "build_command",
    "grade_command",
    "check_latex_command",
    "utils_group",
    "autofill_command",
]
