import pytest
from mcqpy.cli.config import QuizConfig, SelectionConfig
from pathlib import Path

@pytest.fixture
def sample_quiz_config() -> QuizConfig: 
    config = QuizConfig()
    return config

def test_quiz_config_init(sample_quiz_config) -> None:
    assert isinstance(sample_quiz_config, QuizConfig)

def test_quiz_config_example() -> None:
    config = QuizConfig.generate_example_yaml()
    assert isinstance(config, str)

def test_quiz_config_bad_path() -> None:
    with pytest.raises(FileNotFoundError, match="Questions path does not exist"):
        QuizConfig(path=Path('.'), questions_paths=['non_existent_path'])