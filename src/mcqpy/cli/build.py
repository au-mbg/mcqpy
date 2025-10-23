import rich_click as click
from mcqpy.cli.main import main
from mcqpy.cli.config import QuizConfig
from pathlib import Path

from mcqpy.create import MultipleChoiceQuiz
from mcqpy.question import QuestionBank

from rich.pretty import Pretty
from rich.console import Console

@main.command(name="build", help="Build the quiz PDF from question files")
@click.option("-c", "--config", type=click.Path(exists=True, path_type=Path), default="config.yaml", help="Path to the config file", show_default=True)
def build_command(config):
    config = QuizConfig.read_yaml(config)
    question_bank = QuestionBank.from_directories(config.questions_paths)

    file_path = Path(config.output_directory) / config.file_name

    questions = question_bank.get_all_questions()

    console = Console()
    console.print("[bold green]Quiz Configuration:[/bold green]")
    console.print(Pretty(config))
    console.print(f"[bold green]Total Questions Loaded:[/bold green] {len(questions)}")


    mcq = MultipleChoiceQuiz(
        document=None,
        file=file_path,
        questions=questions,
        front_matter=config.front_matter,
        header_footer=config.header,
    )

    mcq.build(generate_pdf=True)


