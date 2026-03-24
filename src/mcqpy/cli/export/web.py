"""Export browser-ready quiz bundles."""

from __future__ import annotations

from pathlib import Path

import rich_click as click
from rich.console import Console

from mcqpy.cli._selection import select_questions
from mcqpy.cli.config import QuizConfig
from mcqpy.cli.export.main import export_group
from mcqpy.question import QuestionBank
from mcqpy.web import build_web_quiz_bundle


def _default_web_output_dir(config: QuizConfig) -> Path:
    quiz_stem = Path(config.file_name).stem
    return config.output_directory / "web" / quiz_stem


@export_group.command(name="web", help="Export a static web quiz bundle.")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    show_default=True,
    help="Path to the quiz config file.",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for the exported bundle. Defaults to output/web/<quiz-name>/.",
)
@click.option(
    "--asset-base-url",
    default=None,
    help="Optional published base URL used to rewrite copied local assets.",
)
def export_web_command(
    config: Path,
    output_dir: Path | None,
    asset_base_url: str | None,
) -> None:
    """Export selected questions as a browser-ready quiz bundle."""

    quiz_config = QuizConfig.read_yaml(config)
    target_dir = output_dir or _default_web_output_dir(quiz_config)
    target_dir.mkdir(parents=True, exist_ok=True)

    question_bank = QuestionBank.from_directories(
        quiz_config.questions_paths,
        seed=quiz_config.selection.seed,
    )
    questions = select_questions(question_bank, quiz_config.selection)

    bundle = build_web_quiz_bundle(
        questions,
        title=quiz_config.front_matter.title or Path(quiz_config.file_name).stem,
        description=quiz_config.front_matter.exam_information,
        source=str(config),
        asset_dir=target_dir / "assets",
        asset_base_url=asset_base_url,
    )
    bundle_path = bundle.save_to_file(target_dir / "quiz.json")

    console = Console()
    console.print(f"[bold green]Exported web bundle:[/bold green] {bundle_path}")
    console.print(f"[bold green]Questions:[/bold green] {len(bundle.questions)}")
    console.print(f"[bold green]Assets directory:[/bold green] {target_dir / 'assets'}")
