"""
Definition of the QuestionBank class for managing multiple-choice questions.
"""

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from mcqpy_core.question.filter.base_filter import BaseFilter, CompositeFilter
from mcqpy_core.question.question import Question


@dataclass(frozen=True)
class BankItem:
    question: Question
    path: Path


class QuestionBank:
    """
    A collection of multiple-choice questions with filtering and retrieval capabilities.
    """

    def __init__(self, items: list[BankItem], seed: int | None = None):
        self._items = items
        self._by_slug = {it.question.slug: it for it in items}
        self._by_qid = {it.question.qid: it for it in items}
        self._rng = random.Random(seed)
        self._filters = []

    @classmethod
    def from_questions(cls, questions: list[Question], **kwargs):
        """
        Create a QuestionBank from a list of Question objects.

        Parameters
        ------------
        questions:
            List of Question instances to include in the bank
        """
        items = [BankItem(question=q, path=None) for q in questions]
        return cls(items=items, **kwargs)

    @classmethod
    def from_directories(
        cls,
        directories: list[str],
        glob_pattern="*.yaml",
        progress_bar: bool = False,
        **kwargs,
    ):
        """
        Create a QuestionBank by loading questions from specified directories.
        Ensures no duplicate slugs are present.

        Parameters
        ------------
        directories:
            List of directory paths to load questions from
        glob_pattern:
            Glob pattern to match question files (default: '*.yaml')
        """
        if progress_bar:
            from rich.progress import track
        else:
            track = lambda x, **kwargs: x  # No-op if progress bar is disabled

        items = []
        qids, slugs = set(), set()
        for directory in directories:
            p = Path(directory)
            globbed_files = list(p.glob(glob_pattern))
            for file_path in track(
                globbed_files,
                description="Loading questions",
                total=len(globbed_files),
                transient=True,
            ):
                question = Question.load_yaml(file_path)

                if question.slug in slugs:
                    raise ValueError(
                        f"Duplicate slug found: {question.slug} - {file_path}"
                    )

                slugs.add(question.slug)
                qids.add(question.qid)
                items.append(BankItem(question, file_path))

        return cls(items=items, **kwargs)

    def get_by_slug(self, slug: str) -> Question:
        """
        Retrieve a question by its slug.

        Parameters
        ------------
        slug:
            The slug identifier of the question
        """
        if slug not in self._by_slug:
            raise KeyError(f"Slug {slug} not found in question bank")
        return self._by_slug[slug].question

    def get_by_qid(self, qid: str) -> Question:
        """
        Retrieve a question by its QID.

        Parameters
        ------------
        qid:
            The QID identifier of the question
        """
        if qid not in self._by_qid:
            raise KeyError(f"QID {qid} not found in question bank")
        return self._by_qid[qid].question

    def __len__(self) -> int:
        return len(self._items)

    def get_all_tags(self) -> dict[str, int]:
        """
        Retrieve all tags in the question bank along with their counts.
        """
        tags_count = {}
        for question in self.get_all_questions():
            if question.tags:
                for tag in question.tags:
                    tags_count[tag] = tags_count.get(tag, 0) + 1
        return tags_count

    def get_all_questions(self) -> list[Question]:
        """
        Retrieve all questions in the bank.
        """
        return [item.question for item in self._items]

    def add_filter(self, filter: BaseFilter):
        """
        Add a filter to the question bank.

        Parameters
        ------------
        filter:
            An instance of BaseFilter to apply when retrieving questions
        """
        self._filters.append(filter)

    def get_filtered_questions(
        self,
        number_of_questions: int | None = None,
        shuffle: bool = False,
        sorting: Literal["none", "slug"] = "none",
    ) -> list[Question]:
        """
        Retrieve questions after applying all added filters.

        Parameters
        ------------
        number_of_questions:
            Maximum number of questions to return (None for all)
        shuffle:
            If True, shuffle the questions before returning
        sorting:
            Sorting method: 'none' for no sorting, 'slug' to sort by slug
        """
        if not self._filters:
            questions = self.get_all_questions()
        else:
            for f in self._filters:
                f.set_rng(self._rng)

            comp_filter = CompositeFilter(self._filters)
            questions = comp_filter.apply(self.get_all_questions())

        if shuffle:
            questions = list(questions)
            self._rng.shuffle(questions)

        if number_of_questions is not None:
            questions = questions[:number_of_questions]

        if sorting == "slug":
            questions = sorted(questions, key=lambda q: q.slug)
        elif sorting == "none":
            pass  # No sorting

        return questions


__all__ = ["QuestionBank", "BankItem"]
