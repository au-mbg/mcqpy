"""Command registration for mcqpy-core."""

from mcqpy_core.cli.main import main
from mcqpy_core.cli.export import export_group
from mcqpy_core.cli.export.token import decode_token_command, encode_token_command
from mcqpy_core.cli.export.web import export_web_command
from mcqpy_core.cli.init import init_command
from mcqpy_core.cli.question import question_group
from mcqpy_core.cli.utils.check_filter import check_filter_command
from mcqpy_core.cli.utils.main import utils_group


def register_core_commands(parent) -> None:
    for name, command in main.commands.items():
        parent.add_command(command, name)


__all__ = [
    "register_core_commands",
    "main",
    "init_command",
    "export_group",
    "export_web_command",
    "encode_token_command",
    "decode_token_command",
    "question_group",
    "utils_group",
    "check_filter_command",
]
