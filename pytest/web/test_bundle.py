from pathlib import Path

from mcqpy_core.web import (
    WebQuizBundle,
    build_web_quiz_bundle,
    decode_quiz_token,
    encode_quiz_token,
    grade_web_quiz,
)


def test_build_web_bundle_schema(question_factory, tmp_path):
    question = question_factory(image=True, code=True, tags=["algebra"])
    bundle = build_web_quiz_bundle(
        [question],
        title="Sample Quiz",
        description="Quiz description",
        asset_dir=tmp_path / "assets",
    )

    assert bundle.schema_version == "1.0"
    assert bundle.metadata.title == "Sample Quiz"
    assert len(bundle.questions) == 1

    exported = bundle.questions[0]
    assert exported.slug == question.slug
    assert exported.qid == question.qid
    assert exported.point_value == question.point_value
    assert exported.correct_onehot.count(1) == len(question.correct_answers)
    assert exported.images
    assert exported.images[0].startswith("assets/")
    assert exported.code_blocks
    assert exported.has_explanation is True
    assert not hasattr(exported, "comment")
    assert not hasattr(exported, "path")


def test_build_web_bundle_copies_local_assets(question_factory, tmp_path):
    question = question_factory(image=2)
    bundle = build_web_quiz_bundle(
        [question],
        title="Asset quiz",
        asset_dir=tmp_path / "assets",
    )

    images = bundle.questions[0].images
    assert len(images) == 2
    for image in images:
        assert (tmp_path / image).exists()


def test_build_web_bundle_converts_mintinline(question_factory):
    question = question_factory()
    question = question.model_copy(
        update={
            "text": r"Compute \mintinline{python}{x = 1} and report the result."
        }
    )

    bundle = build_web_quiz_bundle([question], title="Inline code quiz")

    assert bundle.questions[0].text == "Compute `x = 1` and report the result."


def test_bundle_round_trip(question_factory, tmp_path):
    bundle = build_web_quiz_bundle(
        [question_factory()],
        title="Round trip quiz",
        asset_dir=tmp_path / "assets",
    )
    path = tmp_path / "quiz.json"
    bundle.save_to_file(path)

    loaded = WebQuizBundle.load_from_file(path)
    assert loaded == bundle


def test_grade_web_quiz_strict(question_factory):
    question = question_factory()
    bundle = build_web_quiz_bundle([question], title="Scored quiz")
    correct_index = bundle.questions[0].correct_onehot.index(1)
    correct_answer = chr(65 + correct_index)

    result = grade_web_quiz(bundle, {question.qid: correct_answer})

    assert result.points == question.point_value
    assert result.max_points == question.point_value
    assert result.question_results[0].correct is True


def test_grade_web_quiz_blank_and_partial(question_factory):
    question = question_factory()
    question_multi = question_factory()
    question_multi = question_multi.model_copy(
        update={
            "question_type": "multiple",
            "correct_answers": [0, 1],
        }
    )

    bundle = build_web_quiz_bundle([question, question_multi], title="Blank quiz")
    result = grade_web_quiz(
        bundle,
        {
            question.qid: None,
            question_multi.qid: ["A"],
        },
    )

    assert result.points == 0
    assert result.max_points == question.point_value + question_multi.point_value
    assert [item.correct for item in result.question_results] == [False, False]


def test_token_round_trip():
    url = "https://example.github.io/course/quiz.json"
    token = encode_quiz_token(url)

    assert token.startswith("mcqpy:")
    assert decode_quiz_token(token) == url


def test_token_decode_rejects_invalid_prefix():
    try:
        decode_quiz_token("not-a-token")
    except ValueError as exc:
        assert "mcqpy:" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected invalid token to raise ValueError.")
