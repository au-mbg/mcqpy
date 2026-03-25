"""Generate wheel-based Shinylive snippets for Quarto."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_BROWSER_REQUIREMENTS = ("shiny>=1.2.1",)


def _py_literal(value):
    return repr(value)


def _app_lines(
    *,
    fixed_url: str | None,
    fixed_token: str | None,
    allow_manual_load: bool,
    title: str,
    card_width: str,
) -> list[str]:
    return [
        "from mcqpy_shiny.embed_app import create_app",
        "",
        "app = create_app(",
        f"    fixed_url={_py_literal(fixed_url)},",
        f"    fixed_token={_py_literal(fixed_token)},",
        f"    allow_manual_load={allow_manual_load},",
        f"    title={_py_literal(title)},",
        f"    card_width={_py_literal(card_width)},",
        ")",
    ]


def _requirements_text(
    *,
    wheel_url: str,
    extra_requirements: list[str] | None,
) -> str:
    requirements: list[str] = list(DEFAULT_BROWSER_REQUIREMENTS)

    if extra_requirements:
        for requirement in extra_requirements:
            if requirement not in requirements:
                requirements.append(requirement)

    requirements.append(wheel_url)
    return "\n".join(requirements)


def build_embed_qmd(
    *,
    fixed_url: str | None,
    fixed_token: str | None,
    allow_manual_load: bool,
    title: str,
    card_width: str,
    wheel_url: str,
    extra_requirements: list[str] | None = None,
) -> str:
    parts = [
        "```{shinylive-python}",
        "#| standalone: true",
        "## file: app.py",
        *_app_lines(
            fixed_url=fixed_url,
            fixed_token=fixed_token,
            allow_manual_load=allow_manual_load,
            title=title,
            card_width=card_width,
        ),
        "## file: requirements.txt",
        _requirements_text(wheel_url=wheel_url, extra_requirements=extra_requirements),
        "```",
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a wheel-based Shinylive-ready Quarto snippet."
    )
    parser.add_argument("--output", required=True, help="Output .qmd snippet path.")
    parser.add_argument("--fixed-url", default=None, help="Fixed quiz bundle URL.")
    parser.add_argument("--fixed-token", default=None, help="Fixed quiz token.")
    parser.add_argument(
        "--allow-manual-load",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Allow the user to replace the fixed quiz with a link/token.",
    )
    parser.add_argument("--title", default="MCQPy Quiz", help="Displayed app title.")
    parser.add_argument("--card-width", default="900px", help="Desktop card width.")
    parser.add_argument(
        "--wheel-url",
        required=True,
        help="Full public wheel URL for mcqpy-shiny.",
    )
    parser.add_argument(
        "--extra-requirement",
        action="append",
        default=[],
        help="Additional requirements.txt entries to include.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_embed_qmd(
            fixed_url=args.fixed_url,
            fixed_token=args.fixed_token,
            allow_manual_load=args.allow_manual_load,
            title=args.title,
            card_width=args.card_width,
            wheel_url=args.wheel_url,
            extra_requirements=args.extra_requirement,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
