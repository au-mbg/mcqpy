import rich_click as click
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig
from pathlib import Path

from mcqpy.grade import MCQGrader, get_grade_dataframe
from mcqpy.create.manifest import Manifest
from mcqpy.grade.rubric import StrictRubric
from rich.progress import track


@main.command(name="grade", help="Grade student submissions")
@click.option("-c", "--config", type=click.Path(exists=True, path_type=Path), default="config.yaml", help="Path to the config file", show_default=True)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-f", "--file-format", type=click.Choice(["xlsx", "csv"]), default="xlsx", help="Output format for the grades", show_default=True)
@click.option('-a', '--analysis', is_flag=True, help="Generate question analysis reports", default=False)
def grade_command(config, verbose: bool, file_format: str, analysis: bool):

    # Load config
    config = QuizConfig.read_yaml(config)
    file_name = Path(config.file_name).stem
    manifest_path = Path(config.output_directory) / f"{file_name}_manifest.json"
    manifest = Manifest.load_from_file(manifest_path)

    # Read & Grade submissions
    graded_sets = []    
    submissions = list(Path(config.submission_directory).glob("*.pdf"))
    for submission in track(submissions, description=f"Grading submissions ({len(submissions)})", total=len(submissions)):
        grader = MCQGrader(manifest, StrictRubric())
        graded_set = grader.grade(submission)
        graded_sets.append(graded_set)

    # Export grades to dataframe
    df = get_grade_dataframe(graded_sets)
    output_path = Path(config.submission_directory).parent / f"{file_name}_grades.{file_format}"
    if file_format == "xlsx":
        df.to_excel(output_path, index=False)
    elif file_format == "csv":
        df.to_csv(output_path, index=False)

    if analysis:
        from mcqpy.grade.analysis import question_analysis    
        analysis_directory = Path('analysis/')
        analysis_directory.mkdir(exist_ok=True)
        for qidx in track(range(len(graded_sets[0].graded_questions)), description="Generating question analyses", total=len(graded_sets[0].graded_questions)):
            question_analysis([gs.graded_questions[qidx] for gs in graded_sets], out_directory=analysis_directory)
