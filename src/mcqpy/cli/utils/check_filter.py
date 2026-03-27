"""Compatibility shim for the filter-check CLI command now owned by mcqpy-core."""

from mcqpy_core.cli.utils.check_filter import check_filter_command

__all__ = ["check_filter_command"]
