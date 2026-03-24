"""CLI group for web export utilities."""

import rich_click as click

from mcqpy.cli.main import main


@main.group(name="export")
def export_group() -> None:
    """Commands for exporting browser-ready quiz artifacts."""
    return None  # pragma: no cover
