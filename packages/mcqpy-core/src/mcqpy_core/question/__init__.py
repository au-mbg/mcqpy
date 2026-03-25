"""
MCQPy Question Module
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from .utils import (
    compute_question_sha256,
    _norm_images,
    _norm_opts,
    _norm_caps,
    Image,
    ImageOptions,
    ImageCaptions,
    relativize_paths
)
from .question import Question

if TYPE_CHECKING:
    from .question_bank import QuestionBank


__all__ = ["Question", "QuestionBank", "compute_question_sha256"]


def __getattr__(name: str):
    if name == "QuestionBank":
        return import_module("mcqpy_core.question.question_bank").QuestionBank
    raise AttributeError(name)
