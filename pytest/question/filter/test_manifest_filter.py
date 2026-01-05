import pytest
from mcqpy.question.filter import ManifestFilter
from mcqpy.compile.manifest import Manifest, ManifestItem

@pytest.fixture
def manifest(question_set_with_meta):
    items = [ManifestItem.from_question(q, None) for q in question_set_with_meta[0:15]]
    manifest = Manifest(items=items)

    return manifest

@pytest.fixture
def manifest_path(tmp_path, manifest):
    path = tmp_path / "manifest.json"
    manifest.save_to_file(path)
    return path

def test_manifest_filter_error():
    with pytest.raises(ValueError):
        ManifestFilter()

def test_manifest_filter(manifest, question_set_with_meta):
    manifest_filter = ManifestFilter(manifest=manifest)
    filtered_questions = manifest_filter.apply(question_set_with_meta)
    assert len(filtered_questions) == 5

def test_manifest_filter_exclude_false(manifest, question_set_with_meta):
    manifest_filter = ManifestFilter(manifest=manifest, exclude=False)
    filtered_questions = manifest_filter.apply(question_set_with_meta)
    assert len(filtered_questions) == 15

def test_manifest_filter_path(manifest_path, question_set_with_meta):
    manifest_filter = ManifestFilter(manifest_path=manifest_path)
    filtered_questions = manifest_filter.apply(question_set_with_meta)
    assert len(filtered_questions) == 5




