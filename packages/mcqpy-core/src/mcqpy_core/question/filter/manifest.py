"""Module for manifest-based question filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcqpy_core.question.filter.base_filter import BaseFilter

if TYPE_CHECKING:
    from mcqpy_core.manifest import Manifest
    from mcqpy_core.question.question import Question


class ManifestFilter(BaseFilter):
    """
    Manifest file based filter for questions.
    """
    def __init__(
        self,
        manifest: "Manifest" | None = None,
        manifest_path: str | None = None,
        exclude: bool = True,
    ):
        """
        Filter questions based on a manifest file.

        The primary use case is to exclude questions that are listed in a manifest,
        such as questions used in a previous exam/quiz.

        Parameters
        ------------
        manifest: 
            An instance of Manifest. If provided, it will be used directly.
        manifest_path: 
            Path to the manifest file. Used if `manifest` is None.
        exclude: 
            If True, questions in the manifest are excluded.
        """

        if manifest is not None:
            self.manifest = manifest
        elif manifest_path is not None:
            from mcqpy_core.manifest import Manifest

            self.manifest = Manifest.load_from_file(manifest_path)
        else:
            raise ValueError("Either manifest or manifest_path must be provided.")

        self.exclude = exclude

    def apply(self, questions: list["Question"]) -> list["Question"]:
        filtered_questions = []
        manifest_qids = {item.qid for item in self.manifest.items}

        for question in questions:
            if question.qid in manifest_qids:
                if not self.exclude:
                    filtered_questions.append(question)
            else:
                if self.exclude:
                    filtered_questions.append(question)

        return filtered_questions
