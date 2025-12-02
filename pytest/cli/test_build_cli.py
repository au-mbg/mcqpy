import pytest


@pytest.mark.requires_latex
def test_build_exit_code(built_project) -> None:
    assert built_project.exit_code == 0


@pytest.mark.requires_latex
def test_build_pdf_exists(built_pdf_path) -> None:
    assert built_pdf_path.exists()


@pytest.mark.requires_latex
def test_build_pdf_non_empty(built_pdf_path) -> None:
    assert built_pdf_path.stat().st_size > 0


@pytest.mark.requires_latex
def test_build_manifest_exists(built_manifest_path) -> None:
    assert built_manifest_path.exists()


@pytest.mark.requires_latex
def test_build_manifest_non_empty(built_manifest_path) -> None:
    assert built_manifest_path.stat().st_size > 0
