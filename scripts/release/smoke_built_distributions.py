"""Run isolated smoke checks against built distribution artifacts."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    from scripts.release.select_publish_files import discover_artifacts
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from select_publish_files import discover_artifacts


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True)


def smoke_artifact(artifact: Path) -> None:
    filename = artifact.name
    if filename.startswith("mcqpy-"):
        run_command(
            [
                "uv",
                "run",
                "--isolated",
                "--no-project",
                "--with",
                str(artifact),
                "pytest/smoke_test.py",
            ]
        )
        return

    if filename.startswith("mcqpy_core-"):
        code = (
            "from mcqpy_core.question import Question; "
            "from mcqpy_core.web import WebQuizBundle, decode_quiz_token, encode_quiz_token, grade_web_quiz; "
            "print(Question, WebQuizBundle, decode_quiz_token, encode_quiz_token, grade_web_quiz)"
        )
    elif filename.startswith("mcqpy_pdf-"):
        code = (
            "from mcqpy_pdf import MCQPDFParser, grade_pdf; "
            "print(MCQPDFParser, grade_pdf)"
        )
    elif filename.startswith("mcqpy_shiny-"):
        code = (
            "import mcqpy_shiny; "
            "from mcqpy_shiny.embed_app import create_app; "
            "print(mcqpy_shiny.create_app, create_app)"
        )
    else:
        raise ValueError(f"Unsupported artifact: {artifact}")

    run_command(
        [
            "uv",
            "run",
            "--isolated",
            "--no-project",
            "--with",
            str(artifact),
            "python",
            "-c",
            code,
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run smoke tests against all built monorepo distribution artifacts."
    )
    parser.add_argument("--dist-dir", default="dist", help="Directory containing built artifacts.")
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir)
    for artifact in discover_artifacts(dist_dir):
        smoke_artifact(artifact.path)


if __name__ == "__main__":
    main()
