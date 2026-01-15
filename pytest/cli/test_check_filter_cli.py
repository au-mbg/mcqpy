import pytest
from click.testing import CliRunner
from mcqpy.cli.utils.check_filter import check_filter_command
from mcqpy.cli.config import QuizConfig, SelectionConfig
import yaml

@pytest.fixture
def correct_filter_yaml():
    return r"tag: {tags: [math, algebra]}"

@pytest.fixture
def incorrect_filter_yaml():
    return r"tag: {tagss: [math, algebra]}"

@pytest.fixture
def config_file(tmp_path):

    selection_config = SelectionConfig(filters={"tag": {"tags": ["math", "algebra"]}})

    quiz_config = QuizConfig(selection=selection_config, questions_paths=[])
    config_content = yaml.dump(quiz_config.model_dump())

    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)

    return config_path

@pytest.fixture
def split_filter_yaml():
    return ['-fn', 'tag', '-fp', r'{tags: [math, algebra]}']

@pytest.fixture(params=["correct_filter_yaml", "config_file", "split_filter_yaml"])
def successful_invocation(request):
    runner = CliRunner()
    
    if request.param == "correct_filter_yaml":
        yaml_str = request.getfixturevalue("correct_filter_yaml")
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
    elif request.param == "config_file":  # config_file
        config_path = request.getfixturevalue("config_file")
        result = runner.invoke(check_filter_command, ['-c', str(config_path)])
    else:  # split_filter_yaml
        split_args = request.getfixturevalue("split_filter_yaml")
        result = runner.invoke(check_filter_command, split_args)
    
    return result

@pytest.fixture
def unsuccessful_invocation(incorrect_filter_yaml):
    runner = CliRunner()
    result = runner.invoke(check_filter_command, ['-y', incorrect_filter_yaml])
    return result

@pytest.fixture
def usage_error_invocation():
    runner = CliRunner()
    result = runner.invoke(check_filter_command, [])
    return result

def test_check_filter_command_success(successful_invocation):
    assert successful_invocation.exit_code == 0

def test_check_filter_command_failure(unsuccessful_invocation):
    assert unsuccessful_invocation.exit_code == 0
    assert "is invalid" in unsuccessful_invocation.output

def test_check_filter_command_usage_error(usage_error_invocation):
    assert usage_error_invocation.exit_code != 0
    assert "Error" in usage_error_invocation.output