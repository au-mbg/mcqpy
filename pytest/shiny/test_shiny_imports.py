def test_mcqpy_shiny_imports() -> None:
    import mcqpy_shiny

    assert hasattr(mcqpy_shiny, "create_app")
