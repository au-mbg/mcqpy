"""Run isolated smoke checks against built distribution artifacts."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

try:
    from scripts.release.select_publish_files import discover_artifacts
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from select_publish_files import discover_artifacts


def run_command(args: list[str]) -> None:
    env = os.environ.copy()
    env.setdefault("UV_CACHE_DIR", "/tmp/uv-cache")
    subprocess.run(args, check=True, env=env)

def smoke_artifact(artifact_map: dict[str, Path], project_name: str) -> None:
    artifact = artifact_map[project_name]
    with_args: list[str] = []
    if project_name == "mcqpy":
        with_args.extend(
            [
                "--with",
                str(artifact_map["mcqpy-core"]),
                "--with",
                str(artifact_map["mcqpy-pdf"]),
            ]
        )
        run_command(
            [
                "uv",
                "run",
                "--isolated",
                "--no-project",
                *with_args,
                "--with",
                str(artifact),
                "pytest/smoke_test.py",
            ]
        )
        return

    if project_name == "mcqpy-core":
        code = (
            "from mcqpy_core.question import Question; "
            "from mcqpy_core.web import WebQuizBundle, decode_quiz_token, encode_quiz_token, grade_web_quiz; "
            "print(Question, WebQuizBundle, decode_quiz_token, encode_quiz_token, grade_web_quiz)"
        )
    elif project_name == "mcqpy-pdf":
        with_args.extend(["--with", str(artifact_map["mcqpy-core"])])
        code = (
            "from mcqpy_pdf import MCQPDFParser, grade_pdf; "
            "print(MCQPDFParser, grade_pdf)"
        )
    elif project_name == "mcqpy-shiny":
        with_args.extend(["--with", str(artifact_map["mcqpy-core"])])
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
            *with_args,
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
    wheel_artifacts = [
        artifact for artifact in discover_artifacts(dist_dir) if artifact.path.suffix == ".whl"
    ]
    artifact_map = {artifact.project_name: artifact.path for artifact in wheel_artifacts}
    required_projects = {"mcqpy", "mcqpy-core", "mcqpy-pdf", "mcqpy-shiny"}
    missing_projects = sorted(required_projects - artifact_map.keys())
    if missing_projects:
        missing = ", ".join(missing_projects)
        raise SystemExit(f"Missing built wheels for: {missing}")

    for project_name in sorted(required_projects):
        smoke_artifact(artifact_map, project_name)


if __name__ == "__main__":
    main()
