"""Grade student submissions from a quiz."""

from pathlib import Path

import rich_click as click
from mcqpy_core.grading import StrictRubric, get_grade_dataframe
from mcqpy_core.grading.types import GradeState
from mcqpy_core.question.question_bank import QuestionBank
from rich.progress import track
from rich.panel import Panel
from rich.console import Console

from mcqpy_pdf.cli.config import QuizConfig
from mcqpy_pdf.cli.main import main
from mcqpy_pdf.compile.manifest import Manifest
from mcqpy_pdf.grader import grade_pdf


@main.command(
    name="grade",
    help="""Grade student submissions.
Generates a grade report in the specified format (Excel or CSV).
Students submissions are expected to be in submission directory specified in the config file.                            
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
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option(
    "-f",
    "--file-format",
    type=click.Choice(["xlsx", "csv"]),
    default="xlsx",
    help="Output format for the grades",
    show_default=True,
)
@click.option(
    "-a",
    "--analysis",
    is_flag=True,
    help="Generate question analysis reports",
    default=False,
)
def grade_command(config, verbose: bool, file_format: str, analysis: bool):
    """
    Grade student submissions based on the provided configuration file.
    Generates a grade report in the specified format (Excel or CSV).
    Students submissions are expected to be in submission directory specified in the config file.

    Provides the CLI command:
    ```
    mcqpy grade --config config.yaml --file-format xlsx --analysis
    ```
    """
    # Load config
    console = Console()
    config = QuizConfig.read_yaml(config)
    manifest_path = config.output_directory / f"{config.file_path.stem}_manifest.json"
    manifest = Manifest.load_from_file(manifest_path)

    # Read & Grade submissions
    graded_sets = []
    submissions = list(config.submission_directory.glob("*.pdf"))
    faulty_submissions = []
    for submission in track(
        submissions,
        description=f"Grading submissions ({len(submissions)})",
        total=len(submissions),
    ):
        grade_result = grade_pdf(
            submission,
            manifest=manifest,
            rubric=StrictRubric(),
            regex_pattern=config.grading.anonymous_pattern,
        )

        if grade_result.state == GradeState.READER_ERROR:
            console.print(f"Error grading {submission.name}: {grade_result.error_message}", style="bold red")
            faulty_submissions.append(submission)
            continue

        if verbose:
            if grade_result.other_info is not None:
                text = []
                for info in grade_result.other_info.values():
                    text.append(f"{info}")

                panel = Panel("\n".join(text))
                panel.title = f"Grading info for {submission.name}"
                console.print(panel)

        graded_sets.append(grade_result.graded_set)


    # Report faulty submissions
    if faulty_submissions:
        console.print("\nThe following submissions could not be graded due to errors:", style="bold red")
        for submission in faulty_submissions:
            console.print(f"- {submission.relative_to(Path.cwd())}", style="red")

    # Export grades to dataframe
    df = get_grade_dataframe(graded_sets, sort_key=config.grading.output_sort_key)
    output_path = (
        config.root_directory / f"{config.file_path.stem}_grades.{file_format}"
    )
    if file_format == "xlsx":
        df.to_excel(output_path, index=False)
    elif file_format == "csv":
        df.to_csv(output_path, index=False)

    if analysis:
        from mcqpy_pdf.analysis.report import QuizAnalysis

        analysis_directory = config.root_directory / "analysis/"
        analysis_directory.mkdir(exist_ok=True)

        question_bank = QuestionBank.from_directories(config.questions_paths)
        print(f"Question bank loaded for analysis - {len(question_bank)}")

        quiz_analysis = QuizAnalysis(
            graded_sets,
            question_bank=question_bank,
            output_dir=analysis_directory,
            grading_config=config.grading,
        )
        quiz_analysis.build()
