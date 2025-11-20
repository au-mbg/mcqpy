import rich_click as click


from mcqpy.cli.question.main import question_group


@question_group.command(name="render", help="Validate question files")
@click.argument("path", type=click.Path(exists=True))
def render_command(path):
    from mcqpy.question import Question
    from pylatex import Document
    from mcqpy.build.latex_questions import build_question
    from pathlib import Path
    from rich.console import Console
    import subprocess

    console = Console()
    try:
        question = Question.load_yaml(path)
    except Exception as e:
        console.print(f"[bold red]Error loading question from {path}:[/bold red]")
        console.print(e)
        return 

    name = Path(path).stem
    document = Document(
        documentclass="article",
        geometry_options={
            "paper": "a4paper",
            "includeheadfoot": True,
            "left": "2cm",
            "right": "3cm",
            "top": "2.5cm",
            "bottom": "2.5cm",
        },
    )
    try:
        build_question(document, question, quiz_index=0)
        document.generate_pdf(f"{name}", clean_tex=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Invalid latex for question {path}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error generating question PDF for {path}:[/bold red]")
        console.print(e)
    else:
        console.print(f"[bold green]Generated question PDF at: {name}.pdf[/bold green]")



