def test_mcqpy_pdf_imports() -> None:
    import mcqpy_pdf

    assert hasattr(mcqpy_pdf, "MCQPDFParser")
    assert hasattr(mcqpy_pdf, "grade_pdf")
