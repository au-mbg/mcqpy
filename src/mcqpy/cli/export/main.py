"""Compatibility shim for the export command group now owned by mcqpy-core."""

from mcqpy_core.cli.export.main import export_group

__all__ = ["export_group"]
