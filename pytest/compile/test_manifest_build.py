import pytest
from mcqpy.compile.manifest import Manifest


@pytest.fixture(scope="module")
def manifest_file(built_mcq):
    return built_mcq.file.with_name(built_mcq.file.stem + "_manifest").with_suffix(
            ".json")

@pytest.fixture(scope="module")
def loaded_manifest(manifest_file):
    return Manifest.load_from_file(manifest_file)

@pytest.mark.requires_latex
def test_manifest_generated(manifest_file):
    assert manifest_file.exists()
    assert manifest_file.stat().st_size > 0

@pytest.mark.requires_latex
def test_manifest_loads(loaded_manifest):
    assert len(loaded_manifest.items) == 20

@pytest.mark.requires_latex
def test_manifest_get_item(loaded_manifest):
    qid = loaded_manifest.items[0].qid
    item = loaded_manifest.get_item_by_qid(qid)
    assert item is not None
    assert item.qid == qid

def test_manifest_get_item_not_found(loaded_manifest):
    with pytest.raises(ValueError, match="Item with qid non_existent_qid not found in manifest"):
        loaded_manifest.get_item_by_qid("non_existent_qid")
