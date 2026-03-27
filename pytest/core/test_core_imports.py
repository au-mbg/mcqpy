def test_mcqpy_core_imports() -> None:
    import mcqpy_core

    assert hasattr(mcqpy_core, "Question")
    assert hasattr(mcqpy_core, "Manifest")
