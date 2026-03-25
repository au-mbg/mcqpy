"""Core MCQPy models and logic."""

from importlib import import_module

from .manifest import Manifest, ManifestItem
from .question import Question

__all__ = ["Manifest", "ManifestItem", "Question", "QuestionBank"]


def __getattr__(name: str):
    if name == "QuestionBank":
        return import_module("mcqpy_core.question").QuestionBank
    raise AttributeError(name)
