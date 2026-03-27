from mcqpy_shiny.app import _grade_bundle as grade_local_bundle
from mcqpy_shiny.embed_app import _grade_bundle as grade_embed_bundle


def _sample_bundle() -> dict:
    return {
        "schema_version": "1.0",
        "metadata": {
            "title": "Quiz",
            "description": None,
            "source": None,
        },
        "questions": [
            {
                "qid": "q1",
                "slug": "question-1",
                "text": "Question text",
                "choices": ["A", "B", "C"],
                "question_type": "single",
                "point_value": 2,
                "correct_onehot": [0, 1, 0],
                "images": [],
                "image_captions": {},
                "code_blocks": [],
                "has_explanation": False,
            }
        ],
    }


def test_local_grading_wrapper_accepts_dict_bundle() -> None:
    graded = grade_local_bundle(_sample_bundle(), {"q1": "B"})

    assert graded["points"] == 2
    assert graded["max_points"] == 2
    assert graded["question_results"][0]["correct"] is True


def test_embed_grading_wrapper_accepts_dict_bundle() -> None:
    graded = grade_embed_bundle(_sample_bundle(), {"q1": "A"})

    assert graded["points"] == 0
    assert graded["max_points"] == 2
    assert graded["question_results"][0]["correct"] is False
