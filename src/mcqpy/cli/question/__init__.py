"""Compatibility exports for question CLI commands."""

from mcqpy_core.cli.question import (
    check_tag_command,
    init_command,
    question_group,
    render_command,
    validate_command,
)

__all__ = [
    "question_group",
    "validate_command",
    "init_command",
    "render_command",
    "check_tag_command",
]
