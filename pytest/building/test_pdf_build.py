import pytest

@pytest.mark.requires_latex
def test_has_questions(mcq):
    assert len(mcq.get_questions()) == 20

@pytest.mark.requires_latex
def test_pdf_generated(built_mcq):
    assert built_mcq.file.exists()
    assert built_mcq.file.stat().st_size > 0
