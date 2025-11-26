from unittest.mock import patch
from mcqpy.utils.check_latex import (
    check_latex_command,
    check_latex_installation,
    check_latex_compilation,
    LaTeXCheckResult,
)


def test_check_latex_command_not_found():
    """Test when LaTeX command is not available."""
    with patch("subprocess.check_output", side_effect=FileNotFoundError):
        result = check_latex_command("pdflatex")
        assert result.is_available is False
        assert result.version == "N/A"


def test_check_latex_installation_missing_pdflatex():
    """Test when pdflatex is not installed."""
    with patch(
        "mcqpy.utils.check_latex.check_latex_command",
        return_value=LaTeXCheckResult(
            command="pdflatex", is_available=False, version="N/A"
        ),
    ):
        success, details = check_latex_installation()
        assert success is False
        assert details["pdflatex"].is_available is False

def test_check_latex_compilation_failure():
    """Test when LaTeX compilation fails."""
    with patch(
        "mcqpy.utils.check_latex.check_latex_command",
        side_effect=[
            LaTeXCheckResult(command="pdflatex", is_available=True, version="pdflatex 3.14159265"),
            LaTeXCheckResult(command="latexmk", is_available=True, version="latexmk 4.65"),
        ],
    ), patch(
        "mcqpy.utils.check_latex.check_latex_compilation",
        return_value=(False, "Compilation error"),
    ):
        success, details = check_latex_installation()
        assert success is False
        assert details["compilation_test"] is False
        assert details["error_message"] == "Compilation error"

def test_check_generate_pdf_failure():
    """Test when PDF generation fails during LaTeX compilation check."""
    with patch(
        "pylatex.document.Document.generate_pdf",
        side_effect=Exception("PDF generation failed"),
    ):
        success, error_msg = check_latex_compilation()
        assert success is False
        assert error_msg == "PDF generation failed"

def test_check_pdf_not_created():
    """Test when PDF file is not created after LaTeX compilation."""
    with patch(
        "pylatex.document.Document.generate_pdf",
        return_value=None,
    ), patch(
        "pathlib.Path.exists",
        return_value=False,
    ):
        success, error_msg = check_latex_compilation()
        assert success is False
        assert error_msg == "PDF file was not generated."


def test_check_latex_installation_all_present():
    """
    Test when all LaTeX commands are installed and compilation works.
    This will fail if LaTeX is not actually installed in the test environment.
    """
    success, details = check_latex_installation()
    assert success is True
    assert details["pdflatex"].is_available is True
    assert details["latexmk"].is_available is True
    assert details["compilation_test"] is True
