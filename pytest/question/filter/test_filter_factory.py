from mcqpy.question.filter.factory import FilterFactory
import pytest

@pytest.fixture
def filter_factory():
    return FilterFactory

def test_from_config_difficulty(filter_factory):
    config = {'type': 'difficulty', 'difficulty': '<hard'}
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'DifficultyFilter'
    assert filter_instance.value == 'hard'
    assert filter_instance.operator == '<'

def test_from_config_tags_exclude(filter_factory):
    config = {'type': 'tag', 'tags': ['python'], 'exclude': True}
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'TagFilter'
    assert filter_instance.value == ['python']
    assert filter_instance.exclude is True

def test_from_config_unknown_type(filter_factory):
    config = {'type': 'unknown'}
    with pytest.raises(ValueError) as excinfo:
        filter_factory.from_config(config)
    assert "Unknown filter type: unknown" in str(excinfo.value)

def test_from_config_composite(filter_factory):
    config = {
        'type': 'composite',
        'filters': [
            {'type': 'difficulty', 'difficulty': '>=medium'},
            {'type': 'tag', 'tags': ['math']}
        ]
    }
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'CompositeFilter'
    assert len(filter_instance.filters) == 2