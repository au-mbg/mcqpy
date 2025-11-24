def test_has_questions(mcq):
    assert len(mcq.get_questions()) == 20


def test_pdf_generated(built_mcq):
    assert built_mcq.file.exists()
    assert built_mcq.file.stat().st_size > 0
