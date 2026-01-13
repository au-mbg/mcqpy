import pytest
from mcqpy.cli.config import GradingConfig

def test_grading_config_defaults():
    grading_config = GradingConfig()
    assert isinstance(grading_config, GradingConfig)

def test_grading_config_valid_regex():
    valid_pattern = r"^[a-zA-Z0-9_]+$"
    grading_config = GradingConfig(anonymous_pattern=valid_pattern)
    assert grading_config.anonymous_pattern == valid_pattern

def test_grading_config_invalid_regex():
    invalid_pattern = r"[a-zA-Z0-9_"
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        GradingConfig(anonymous_pattern=invalid_pattern)
