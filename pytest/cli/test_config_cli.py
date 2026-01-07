import pytest
from mcqpy.cli.config import QuizConfig, SelectionConfig

@pytest.fixture
def sample_quiz_config() -> QuizConfig: 
    config = QuizConfig()
    return config

def test_quiz_config_init(sample_quiz_config) -> None:
    assert isinstance(sample_quiz_config, QuizConfig)

def test_quiz_config_example() -> None:
    config = QuizConfig.generate_example_yaml()
    assert isinstance(config, str)

