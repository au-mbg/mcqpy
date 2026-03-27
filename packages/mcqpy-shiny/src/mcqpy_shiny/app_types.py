"""Shared callable types for quiz app construction."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

BundleLoader = Callable[[str], Awaitable[dict]]
TokenDecoder = Callable[[str], str]
BundleGrader = Callable[[dict, dict], dict]
