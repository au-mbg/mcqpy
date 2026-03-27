"""Compatibility shims for selection helpers now owned by mcqpy-core."""

from mcqpy_core.cli._selection import _build_filter, build_filters, select_questions

__all__ = ["select_questions", "_build_filter", "build_filters"]
