"""Web quiz bundle models and export helpers."""

from __future__ import annotations

import re
from pathlib import Path
from shutil import copy2
from urllib.parse import urljoin

from pydantic import BaseModel, ConfigDict, Field

from mcqpy_core.manifest import ManifestItem
from mcqpy_core.question import Question


def _is_remote_asset(path: str) -> bool:
    return path.startswith("http://") or path.startswith("https://")


_MINTINLINE_RE = re.compile(
    r"\\mintinline\{(?P<language>[^{}]+)\}\{(?P<code>[^{}]*)\}"
)


def _convert_inline_markup(text: str) -> str:
    """Convert authoring-only inline markup into browser-friendly Markdown."""

    def _replace_mintinline(match: re.Match[str]) -> str:
        code = match.group("code").replace("`", "\\`")
        return f"`{code}`"

    return _MINTINLINE_RE.sub(_replace_mintinline, text)


class WebQuizMetadata(BaseModel):
    """Metadata shown to learners for a quiz bundle."""

    title: str
    description: str | None = None
    source: str | None = None


class WebQuizCodeBlock(BaseModel):
    """Code block included in a web quiz question."""

    code: str
    language: str | None = None


class WebQuizQuestion(BaseModel):
    """Normalized question payload for web delivery."""

    model_config = ConfigDict(frozen=True)

    qid: str
    slug: str
    text: str
    choices: list[str]
    question_type: str
    point_value: int
    correct_onehot: list[int]
    images: list[str] = Field(default_factory=list)
    image_captions: dict[int, str] = Field(default_factory=dict)
    code_blocks: list[WebQuizCodeBlock] = Field(default_factory=list)
    has_explanation: bool = False


class WebQuizBundle(BaseModel):
    """Stable bundle consumed by the Shiny app."""

    schema_version: str = "1.0"
    metadata: WebQuizMetadata
    questions: list[WebQuizQuestion]

    def save_to_file(self, path: str | Path, indent: int = 2) -> Path:
        output_path = Path(path)
        output_path.write_text(self.model_dump_json(indent=indent), encoding="utf-8")
        return output_path

    @classmethod
    def load_from_file(cls, path: str | Path) -> "WebQuizBundle":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))


class WebQuizQuestionResult(BaseModel):
    """Per-question score for a learner submission."""

    qid: str
    slug: str
    selected_onehot: list[int]
    correct: bool
    points: int
    max_points: int


class WebQuizResult(BaseModel):
    """Aggregate score for a learner submission."""

    points: int
    max_points: int
    question_results: list[WebQuizQuestionResult]


def _copy_local_asset(
    source: str, question: Question, index: int, asset_dir: Path
) -> str:
    source_path = Path(source).resolve()
    suffix = source_path.suffix.lower()
    target_name = f"{question.slug}_{index + 1}{suffix}"
    target_path = asset_dir / target_name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(source_path, target_path)
    return f"assets/{target_name}"


def _normalize_asset_refs(
    question: Question,
    asset_dir: Path | None,
    asset_base_url: str | None,
) -> list[str]:
    refs: list[str] = []
    for index, image_path in enumerate(question.image or []):
        if _is_remote_asset(image_path):
            refs.append(image_path)
            continue

        if asset_dir is None:
            refs.append(str(Path(image_path)))
            continue

        relative_ref = _copy_local_asset(image_path, question, index, asset_dir)
        if asset_base_url:
            refs.append(urljoin(asset_base_url.rstrip("/") + "/", relative_ref))
        else:
            refs.append(relative_ref)
    return refs


def _normalize_code_blocks(question: Question) -> list[WebQuizCodeBlock]:
    if question.code is None:
        return []

    code_entries = question.code if isinstance(question.code, list) else [question.code]
    languages = (
        question.code_language
        if isinstance(question.code_language, list)
        else [question.code_language] * len(code_entries)
    )

    return [
        WebQuizCodeBlock(code=code, language=language)
        for code, language in zip(code_entries, languages, strict=False)
        if code is not None
    ]


def question_to_web_question(
    question: Question,
    asset_dir: Path | None = None,
    asset_base_url: str | None = None,
) -> WebQuizQuestion:
    """Convert an authored question into the normalized web schema."""

    manifest_item = ManifestItem.from_question(question, None)
    return WebQuizQuestion(
        qid=question.qid,
        slug=question.slug,
        text=_convert_inline_markup(question.text),
        choices=list(question.choices),
        question_type=question.question_type,
        point_value=question.point_value,
        correct_onehot=list(manifest_item.correct_onehot),
        images=_normalize_asset_refs(question, asset_dir=asset_dir, asset_base_url=asset_base_url),
        image_captions=dict(question.image_caption or {}),
        code_blocks=_normalize_code_blocks(question),
        has_explanation=bool(question.explanation),
    )


def build_web_quiz_bundle(
    questions: list[Question],
    *,
    title: str,
    description: str | None = None,
    source: str | None = None,
    asset_dir: Path | None = None,
    asset_base_url: str | None = None,
) -> WebQuizBundle:
    """Build a web quiz bundle from authored questions."""

    if asset_dir is not None:
        asset_dir.mkdir(parents=True, exist_ok=True)

    return WebQuizBundle(
        metadata=WebQuizMetadata(title=title, description=description, source=source),
        questions=[
            question_to_web_question(
                question,
                asset_dir=asset_dir,
                asset_base_url=asset_base_url,
            )
            for question in questions
        ],
    )


def _answers_to_onehot(
    answer: str | int | list[str] | list[int] | tuple[str, ...] | tuple[int, ...] | None,
    n_choices: int,
) -> list[int]:
    onehot = [0] * n_choices
    if answer is None:
        return onehot

    selected = list(answer) if isinstance(answer, (list, tuple)) else [answer]
    for item in selected:
        if isinstance(item, int):
            index = item
        else:
            normalized = item.strip().upper()
            index = ord(normalized[0]) - 65

        if 0 <= index < n_choices:
            onehot[index] = 1
    return onehot


def grade_web_quiz(
    bundle: WebQuizBundle, answers: dict[str, str | int | list[str] | list[int] | None]
) -> WebQuizResult:
    """Grade answers against a web quiz bundle with strict matching."""

    question_results: list[WebQuizQuestionResult] = []
    for question in bundle.questions:
        selected_onehot = _answers_to_onehot(answers.get(question.qid), len(question.choices))
        correct = selected_onehot == question.correct_onehot
        points = question.point_value if correct else 0
        question_results.append(
            WebQuizQuestionResult(
                qid=question.qid,
                slug=question.slug,
                selected_onehot=selected_onehot,
                correct=correct,
                points=points,
                max_points=question.point_value,
            )
        )

    return WebQuizResult(
        points=sum(item.points for item in question_results),
        max_points=sum(item.max_points for item in question_results),
        question_results=question_results,
    )
