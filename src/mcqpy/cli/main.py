"""Main module for mcqpy CLI."""
import rich_click as click

from mcqpy_core.cli import register_core_commands
from mcqpy_pdf.cli import register_pdf_commands

@click.group(name="mcqpy")
@click.version_option()
def main() -> None:
    """
    Command line interface for mcqpy.
    """
    return None # pragma: no cover


register_core_commands(main)
register_pdf_commands(main)
