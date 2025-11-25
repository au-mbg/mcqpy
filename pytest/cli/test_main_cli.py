from click.testing import CliRunner

import pytest
from mcqpy.cli import main


@pytest.fixture
def main_invocation_result():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    return result


def test_main_exit_code(main_invocation_result) -> None:
    assert main_invocation_result.exit_code == 0


def test_main_output(main_invocation_result) -> None:
    assert "mcqpy" in main_invocation_result.output
