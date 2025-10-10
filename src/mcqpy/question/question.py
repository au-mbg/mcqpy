from pathlib import Path
from typing import Any, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import uuid

from mcqpy.question import (
    Image,
    ImageOptions,
    ImageCaptions,
    _norm_images,
    _norm_opts,
    _norm_caps,
)

# Commit one namespace UUID for your course/repo (don’t change later)
COURSE_NAMESPACE = uuid.UUID("9f1e0d8c-7f3a-4c02-be3b-3f8f5a2a8f2e")

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".tif", ".tiff"}


def qid_from_slug(slug: str) -> str:
    return str(uuid.uuid5(COURSE_NAMESPACE, slug))


class Question(BaseModel):
    model_config = ConfigDict(
        frozen=True, extra="forbid"
    )  # make instances immutable (optional but helpful)

    # Identity
    slug: str = Field(..., description="Immutable short key chosen at creation")
    qid: str = Field(..., description="Stable UUIDv5 derived from slug")

    # Content
    text: str = Field(..., description="Question text, may contain LaTeX")
    choices: List[str] = Field(..., min_length=2, description="Answer choices")
    correct_answers: List[int] = Field(
        ...,
        min_length=1,
        description="Indices of correct answers in `choices`, 0-based",
    )
    question_type: Literal["single", "multiple"] = Field(
        ...,
        description="Type of question: 'single' for single-choice, 'multiple' for multiple-choice",
    )

    # Images
    image: Image = Field(
        None, description="Path(s) to image file(s) associated with the question"
    )
    image_options: ImageOptions = Field(
        None, description="Options for image(s) display, e.g., width, height"
    )
    image_caption: ImageCaptions = Field(
        None, description="Caption(s) for each image(s), if any"
    )

    # Presentation
    permutation: List[int] | None = Field(
        None,
        description="If provided, specifies a permutation of the choices to present",
    )
    fixed_permutation: bool = Field(
        False, description="If true, do not permute the choices when presenting"
    )

    # Metadata
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_media_fields(cls, data: Any):
        if not isinstance(data, dict):
            return data

        # Pull raw inputs (may be absent/None/union-shaped)
        raw_img = data.get("image")
        raw_opts = data.get("image_options")
        raw_caps = data.get("image_caption")

        # Normalize
        norm_img = _norm_images(raw_img)
        norm_opts = _norm_opts(raw_opts)
        norm_caps = _norm_caps(raw_caps)

        # Optional sanity check: indices referenced by opts/caps must exist in images
        if norm_img:
            max_idx = len(norm_img) - 1
            for src_name, idxs in (
                ("image_options", norm_opts.keys()),
                ("image_captions", norm_caps.keys()),
            ):
                if norm_img and -1 in idxs:
                    continue  # -1 is always valid if we have images (for global caption)
                bad = [i for i in idxs if i < 0 or i > max_idx]
                if bad:
                    raise ValueError(
                        f"{src_name} contains out-of-range indices {bad}; "
                        f"valid range is 0..{max_idx} (got {len(norm_img)} images)."
                    )

        # Write back normalized values so field parsing sees canonical shapes
        data["image"] = norm_img
        data["image_options"] = norm_opts
        data["image_caption"] = norm_caps
        return data

    @model_validator(mode="before")
    @classmethod
    def _derive_qid(cls, data: dict):
        """
        - If qid missing: compute it from slug.
        - If qid provided: verify it matches the computed one.
        """
        if not isinstance(data, dict):
            return data
        if "slug" not in data:
            raise ValueError("slug is required to derive qid")

        expected = qid_from_slug(data["slug"])
        provided = data.get("qid")

        if provided is None:
            data["qid"] = expected
        elif provided != expected:
            raise ValueError(
                f"Provided qid does not match slug-derived qid.\n"
                f"  slug: {data['slug']}\n"
                f"  expected: {expected}\n"
                f"  provided: {provided}"
            )
        return data

    @model_validator(mode="before")
    @classmethod
    def _validate_derive_permutation(cls, data: dict):
        """
        If permutation is not provided, set it to the identity permutation.
        """
        if data.get("permutation") is None:
            data["permutation"] = list(range(len(data["choices"])))
        return data

    @field_validator("image")
    @classmethod
    def validate_image(cls, v: Optional[str], info):
        if not v:
            return v

        if not isinstance(v, list):
            v = [v]

        full_paths = []
        for item in v:
            p = Path(item)
            # Resolve relative to the YAML file directory, if provided via context
            base_dir = info.context.get("base_dir", Path.cwd())
            resolved = p if p.is_absolute() else (base_dir / p).resolve()

            if not resolved.exists() or not resolved.is_file():
                raise ValueError(f"Image not found: {v} (resolved to: {resolved})")
            if resolved.suffix.lower() not in ALLOWED_IMAGE_EXTS:
                raise ValueError(
                    f"Unsupported image extension '{resolved.suffix}'. "
                    f"Allowed: {sorted(ALLOWED_IMAGE_EXTS)}"
                )
            full_paths.append(resolved)

        return full_paths

    @classmethod
    def load_yaml(cls, filepath: str) -> "Question":
        """Load a Question from a YAML file."""
        import yaml

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data, context={"base_dir": Path(filepath).parent})
