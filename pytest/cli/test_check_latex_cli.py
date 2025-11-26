from click.testing import CliRunner
from mcqpy.cli.check_latex import check_latex_command
import pytest
from unittest.mock import patch, MagicMock

from mcqpy.utils.check_latex import LaTeXCheckResult

@pytest.fixture
def successful_invocation():
    runner = CliRunner()
    result = runner.invoke(check_latex_command)
    return result

@pytest.fixture
def unsuccessful_invocation():
    with patch(
        "mcqpy.utils.check_latex.check_latex_command",
        return_value=LaTeXCheckResult(
            command="pdflatex", is_available=False, version="N/A"
        ),
    ):    
        runner = CliRunner()
        result = runner.invoke(check_latex_command)
    return result



def test_check_latex_command(successful_invocation):
    assert successful_invocation.exit_code == 0

def test_check_latex_output(successful_invocation):
    assert "LaTeX is properly installed" in successful_invocation.output

def test_check_latex_failure_output(unsuccessful_invocation):
    assert "LaTeX installation issue" in unsuccessful_invocation.output



