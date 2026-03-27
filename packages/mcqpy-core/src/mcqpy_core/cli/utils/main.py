import rich_click as click
from mcqpy_core.cli.main import main

@main.group(name="utils")
def utils_group() -> None:
    """
    Utility commands for MCQPy.
    """
    return None # pragma: no cover
