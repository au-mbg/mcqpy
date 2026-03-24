"""
CLI Build Command
"""

from pathlib import Path

import rich_click as click
from rich.pretty import Pretty
from rich.console import Console

from mcqpy.cli._selection import select_questions
from mcqpy.cli.config import QuizConfig
from mcqpy.cli.main import main
from mcqpy.compile import MultipleChoiceQuiz
from mcqpy.compile.manifest import Manifest
from mcqpy.question import QuestionBank


# Backward-compatible private alias kept for older tests/importers.
_select_questions = select_questions


def build_solution(questions, manifest, output_path: Path):
    from mcqpy.compile.solution_pdf import SolutionPDF

    solution_pdf = SolutionPDF(file=output_path, questions=questions, manifest=manifest)
    solution_pdf.build(generate_pdf=True)

@main.command(
    name="build",
    help="""Build the quiz PDF from question files based on the provided configuration.
    This command reads the quiz configuration, selects questions from the question bank,
    and generates the quiz PDF along with a solution PDF.
""",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to the config file",
    show_default=True,
)
def build_command(config):
    """ 
    Build the quiz PDF from question files based on the provided configuration.
    This command reads the quiz configuration, selects questions from the question bank,
    and generates the quiz PDF along with a solution PDF.

    ```
    mcqpy build --config config.yaml
    ```
    """

    config = QuizConfig.read_yaml(config)
    question_bank = QuestionBank.from_directories(
        config.questions_paths, seed=config.selection.seed
    )
    questions = select_questions(question_bank, config.selection)

    console = Console()
    console.print("[bold green]Quiz Configuration:[/bold green]")
    console.print(Pretty(config))
    console.print(
        f"[bold green]Total questions in bank:[/bold green] {len(question_bank)}"
    )
    console.print(f"[bold green]Selected questions:[/bold green] {len(questions)}")

    ## Paths:
    for path in [config.root_directory, config.output_directory, config.submission_directory]:
        if path and not path.exists():
            path.mkdir(parents=True, exist_ok=True)  # pragma: no cover

    mcq = MultipleChoiceQuiz(
        file=config.file_path,
        questions=questions,
        front_matter=config.front_matter,
        header_footer=config.header,
    )

    mcq.build(generate_pdf=True)

    # Build solution PDF
    manifest_path = mcq.get_manifest_path()
    manifest = Manifest.load_from_file(manifest_path)
    solution_output_path = (
        config.output_directory / f"{config.file_name.replace('.pdf', '')}_solution.pdf"
    )
    build_solution(questions, manifest, solution_output_path)
