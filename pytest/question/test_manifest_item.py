import pytest
from mcqpy.build.manifest import ManifestItem
from mcqpy.question import Question, compute_question_sha256


@pytest.fixture(params=[0, 1, 2, 3, 4, 5])
def question(request, question_set):
    question = question_set[request.param]
    return question


@pytest.fixture()
def manifest_item(question: Question) -> ManifestItem:
    return ManifestItem.from_question(question, permutation=None)


def test_manifest_qid(manifest_item: ManifestItem, question: Question):
    assert manifest_item.qid == question.qid


def test_manifest_slug(manifest_item: ManifestItem, question: Question):
    assert manifest_item.slug == question.slug


def test_manifest_non_permuted_correct_answers(
    manifest_item: ManifestItem, question: Question
):
    assert manifest_item.non_permuted_correct_answers == question.correct_answers


def test_manifest_permuted_correct_answers(
    manifest_item: ManifestItem, question: Question
):
    expected_permuted_correct_answers = [
        question.permutation.index(i) for i in question.correct_answers
    ]
    assert manifest_item.permuted_correct_answers == expected_permuted_correct_answers


def test_manifest_correct_onehot(manifest_item: ManifestItem, question: Question):
    n_choices = len(question.choices)
    expected_onehot = [0] * n_choices
    for i in question.correct_answers:
        permuted_index = question.permutation.index(i)
        expected_onehot[permuted_index] = 1
    assert manifest_item.correct_onehot == expected_onehot


def test_manifest_point_value(manifest_item: ManifestItem, question: Question):
    assert manifest_item.point_value == question.point_value

def test_manifest_sha256(manifest_item: ManifestItem, question: Question):
    expected_hash = compute_question_sha256(question)
    assert manifest_item.sha256 == expected_hash