import rich_click as click
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig
from pathlib import Path

from mcqpy.compile import MultipleChoiceQuiz
from mcqpy.question import QuestionBank
from mcqpy.compile.manifest import Manifest

from rich.pretty import Pretty
from rich.console import Console

def build_solution(questions, manifest, output_path: Path):
    from mcqpy.compile.solution_pdf import SolutionPDF    
    solution_pdf = SolutionPDF(
        file=output_path,
        questions=questions,
        manifest=manifest
    )

    solution_pdf.build(generate_pdf=True)

@main.command(name="build", help="Build the quiz PDF from question files")
@click.option("-c", "--config", type=click.Path(exists=True, path_type=Path), default="config.yaml", help="Path to the config file", show_default=True)
def build_command(config):
    config = QuizConfig.read_yaml(config)
    question_bank = QuestionBank.from_directories(config.questions_paths)

    file_path = Path(config.output_directory) / config.file_name

    questions = question_bank.get_all_questions()[0:100]

    # If the slugs contain a number sort by that number
    if all(q.slug.split("_")[-1].isdigit() for q in questions):
        questions.sort(key=lambda q: int(q.slug.split("_")[-1]))
    else:
        questions.sort(key=lambda q: q.slug)

    console = Console()
    console.print("[bold green]Quiz Configuration:[/bold green]")
    console.print(Pretty(config))
    console.print(f"[bold green]Total Questions Loaded:[/bold green] {len(questions)}")


    mcq = MultipleChoiceQuiz(
        file=file_path,
        questions=questions,
        front_matter=config.front_matter,
        header_footer=config.header,
    )

    mcq.build(generate_pdf=True)

    # Build solution PDF
    manifest_path = mcq.get_manifest_path()
    manifest = Manifest.load_from_file(manifest_path)
    solution_output_path = Path(config.output_directory) / f"{config.file_name.replace('.pdf', '')}_solution.pdf"
    print(solution_output_path)
    build_solution(questions, manifest, solution_output_path)


