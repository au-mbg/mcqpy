from click.testing import CliRunner
import pytest
from mcqpy.cli.question import validate_command, init_command, render_command

@pytest.fixture
def validate_question(written_questions):
    runner = CliRunner()
    result = runner.invoke(validate_command, [str(path) for path in written_questions])
    return result

@pytest.fixture
def rendered_question(written_questions):
    runner = CliRunner()
    path = str(written_questions[0])
    result = runner.invoke(render_command, [path])
    return result

@pytest.fixture
def initted_question(tmp_path):
    runner = CliRunner()
    result = runner.invoke(init_command, [str(tmp_path / 'sample_question')])
    yield result, tmp_path / 'sample_question'


def test_questions_written(written_questions) -> None:
    for path in written_questions:
        assert path.exists()

def test_validate_exit_code(validate_question) -> None:
    assert validate_question.exit_code == 0

def test_init_exit_code(initted_question) -> None:
    assert initted_question[0].exit_code == 0

def test_init_creates_file(initted_question) -> None:
    _, path = initted_question
    assert path.exists()

def test_render_exit_code(rendered_question) -> None:
    assert rendered_question.exit_code == 0