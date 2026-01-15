import rich_click as click
from rich.console import Console

from mcqpy.cli.question.main import question_group


@question_group.command(name="check-tags", help="Check tags in questions")
@click.argument("path", type=click.Path(exists=True))
def check_tag_command(path):
    from mcqpy.question import QuestionBank
    question_bank = QuestionBank.from_directories([path])

    tags_count = question_bank.get_all_tags()

    console = Console()
    console.print("[bold blue]Tags in question bank:[/bold blue]")
    for tag, count in tags_count.items():
        console.print(f"- {tag}: {count} question(s)")
    
    
