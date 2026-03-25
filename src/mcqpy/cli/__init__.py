"""Umbrella CLI package with compatibility re-exports."""

from mcqpy.cli.build import build_command
from mcqpy_core.cli import decode_token_command, encode_token_command, export_web_command
from mcqpy.cli.grade import grade_command
from mcqpy.cli.init import init_command
from mcqpy.cli.main import main

__all__ = [
    "main",
    "init_command",
    "build_command",
    "grade_command",
    "export_web_command",
    "encode_token_command",
    "decode_token_command",
]
