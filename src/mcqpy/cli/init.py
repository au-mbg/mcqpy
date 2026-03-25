"""Compatibility shim for the init CLI command now owned by mcqpy-core."""

from mcqpy_core.cli.init import init_command

__all__ = ["init_command"]
