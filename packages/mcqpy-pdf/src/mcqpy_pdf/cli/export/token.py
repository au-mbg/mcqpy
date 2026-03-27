"""CLI helpers for quiz link obfuscation tokens."""

from __future__ import annotations

import rich_click as click

from mcqpy_pdf.cli.export.main import export_group
from mcqpy_core.web import decode_quiz_token, encode_quiz_token


@export_group.command(name="encode-token", help="Encode a public quiz bundle URL.")
@click.argument("url")
def encode_token_command(url: str) -> None:
    click.echo(encode_quiz_token(url))


@export_group.command(name="decode-token", help="Decode a quiz token to its public URL.")
@click.argument("token")
def decode_token_command(token: str) -> None:
    click.echo(decode_quiz_token(token))
