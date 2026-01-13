"""Grade student submissions from a quiz."""

import rich_click as click
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig
from pathlib import Path

from mcqpy.grade import MCQGrader, get_grade_dataframe
from mcqpy.compile.manifest import Manifest
from mcqpy.grade.rubric import StrictRubric
from rich.progress import track

from mcqpy.question.question_bank import QuestionBank


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
    config = QuizConfig.read_yaml(config)
    file_name = Path(config.file_name).stem
    manifest_path = Path(config.output_directory) / f"{file_name}_manifest.json"
    manifest = Manifest.load_from_file(manifest_path)

    # Read & Grade submissions
    graded_sets = []
    grader = MCQGrader(
        manifest, StrictRubric(), regex_pattern=config.grading.anonymous_pattern
    )
    submissions = list(Path(config.grading.submission_directory).glob("*.pdf"))
    for submission in track(
        submissions,
        description=f"Grading submissions ({len(submissions)})",
        total=len(submissions),
    ):
        graded_set = grader.grade(submission)
        graded_sets.append(graded_set)

    # Export grades to dataframe
    df = get_grade_dataframe(graded_sets, sort_key=config.grading.output_sort_key)
    output_path = (
        Path(config.grading.submission_directory).parent
        / f"{file_name}_grades.{file_format}"
    )
    if file_format == "xlsx":
        df.to_excel(output_path, index=False)
    elif file_format == "csv":
        df.to_csv(output_path, index=False)

    if analysis:
        from mcqpy.grade.analysis import QuizAnalysis

        analysis_directory = Path("analysis/")
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
