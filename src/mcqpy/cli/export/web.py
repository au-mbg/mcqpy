"""Compatibility shim for the web export command now owned by mcqpy-core."""

from mcqpy_core.cli.export.web import export_web_command

__all__ = ["export_web_command"]
