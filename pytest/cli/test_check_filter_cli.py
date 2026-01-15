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


class TestDocumentedFilterExamples:
    """Tests for filter examples documented in the user guide"""
    
    def test_tag_filter_basic(self):
        """Test basic tag filter example from documentation"""
        runner = CliRunner()
        yaml_str = r"tag: {tags: [tag1, tag2]}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_tag_filter_with_match_all(self):
        """Test tag filter with match_all parameter"""
        runner = CliRunner()
        yaml_str = r"tag: {tags: [tag1, tag2], match_all: true}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_tag_filter_with_exclude(self):
        """Test tag filter with exclude parameter"""
        runner = CliRunner()
        yaml_str = r"tag: {tags: [tag1, tag2], exclude: true}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_tag_filter_with_strict_missing(self):
        """Test tag filter with strict_missing parameter"""
        runner = CliRunner()
        yaml_str = r"tag: {tags: [tag1, tag2], strict_missing: false}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_tag_filter_all_options(self):
        """Test tag filter with all optional parameters"""
        runner = CliRunner()
        yaml_str = r"tag: {tags: [chapter_01], match_all: false, exclude: false, strict_missing: true}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_date_filter_basic(self):
        """Test basic date filter example from documentation"""
        runner = CliRunner()
        yaml_str = r"date: {date_value: '>=01/01/2024'}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_date_filter_with_end_date(self):
        """Test date filter with end_date parameter"""
        runner = CliRunner()
        yaml_str = r"date: {date_value: '>=01/01/2024', end_date: '31/12/2024'}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_date_filter_with_strict_missing(self):
        """Test date filter with strict_missing parameter"""
        runner = CliRunner()
        yaml_str = r"date: {date_value: '<=31/12/2024', strict_missing: false}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_difficulty_filter_basic(self):
        """Test basic difficulty filter example from documentation"""
        runner = CliRunner()
        yaml_str = r"difficulty: {difficulty: 'easy', operator: '=='}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_difficulty_filter_with_operator_prefix(self):
        """Test difficulty filter with operator in difficulty string"""
        runner = CliRunner()
        yaml_str = r"difficulty: {difficulty: '>easy'}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_difficulty_filter_all_difficulties(self):
        """Test difficulty filter with all documented difficulty levels"""
        runner = CliRunner()
        difficulties = ['very easy', 'easy', 'medium', 'hard', 'very hard']
        for difficulty in difficulties:
            yaml_str = fr"difficulty: {{difficulty: '{difficulty}', operator: '=='}}"
            result = runner.invoke(check_filter_command, ['-y', yaml_str])
            assert result.exit_code == 0, f"Failed for difficulty: {difficulty}"
    
    def test_difficulty_filter_all_operators(self):
        """Test difficulty filter with all documented operators"""
        runner = CliRunner()
        operators = ['==', '<', '<=', '>', '>=']
        for operator in operators:
            yaml_str = fr"difficulty: {{difficulty: 'medium', operator: '{operator}'}}"
            result = runner.invoke(check_filter_command, ['-y', yaml_str])
            assert result.exit_code == 0, f"Failed for operator: {operator}"
    
    def test_difficulty_filter_with_strict_missing(self):
        """Test difficulty filter with strict_missing parameter"""
        runner = CliRunner()
        yaml_str = r"difficulty: {difficulty: 'medium', operator: '==', strict_missing: false}"
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_stratified_filter_basic(self):
        """Test stratified filter example from documentation"""
        runner = CliRunner()
        yaml_str = r"""stratified: {
            number_of_questions: 30,
            filter_configs: [
                {type: tag, tags: [chapter_01]},
                {type: tag, tags: [chapter_02]}
            ],
            proportions: [1, 2]
        }"""
        result = runner.invoke(check_filter_command, ['-y', yaml_str])
        assert result.exit_code == 0
    
    def test_manifest_filter_basic(self):
        """Test manifest filter example from documentation"""
        runner = CliRunner()
        # Create a temporary manifest file
        import tempfile
        import json
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = f"{tmp_dir}/manifest.json"
            with open(manifest_path, "w") as f:
                json.dump({"questions": []}, f)
            
            yaml_str = fr"manifest: {{manifest_path: '{manifest_path}', exclude: true}}"
            result = runner.invoke(check_filter_command, ['-y', yaml_str])
            assert result.exit_code == 0
    
    def test_manifest_filter_exclude_false(self):
        """Test manifest filter with exclude set to false"""
        runner = CliRunner()
        import tempfile
        import json
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = f"{tmp_dir}/manifest.json"
            with open(manifest_path, "w") as f:
                json.dump({"questions": []}, f)
            
            yaml_str = fr"manifest: {{manifest_path: '{manifest_path}', exclude: false}}"
            result = runner.invoke(check_filter_command, ['-y', yaml_str])
            assert result.exit_code == 0