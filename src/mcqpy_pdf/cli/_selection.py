"""Shared question-selection helpers for CLI commands."""

from __future__ import annotations

from mcqpy_pdf.cli.config import SelectionConfig
from mcqpy_core.question import QuestionBank
from mcqpy_core.question.filter import FilterFactory


def _build_filter(filter_name: str, filter_params: dict):
    filter_config = {"type": filter_name, **filter_params}
    return FilterFactory.from_config(filter_config)


def build_filters(selection_config: SelectionConfig):
    filter_objs = []
    if selection_config.filters:
        for filter_name, filter_params in selection_config.filters.items():
            filter_objs.append(_build_filter(filter_name, filter_params))
    return filter_objs


def select_questions(question_bank: QuestionBank, selection_config: SelectionConfig):
    for filter_obj in build_filters(selection_config):
        question_bank.add_filter(filter_obj)

    return question_bank.get_filtered_questions(
        number_of_questions=selection_config.number_of_questions,
        shuffle=selection_config.shuffle,
        sorting=selection_config.sort_type,
    )
