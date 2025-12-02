from mcqpy.question.filter.factory import FilterFactory
import pytest

@pytest.fixture
def filter_factory():
    return FilterFactory

def test_from_config_difficulty(filter_factory):
    config = {'type': 'difficulty', 'value': '<hard'}
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'DifficultyFilter'
    assert filter_instance.value == 'hard'
    assert filter_instance.operator == '<'

def test_from_config_tags_exclude(filter_factory):
    config = {'type': 'tags', 'value': ['python'], 'exclude': True}
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'TagFilter'
    assert filter_instance.value == ['python']
    assert filter_instance.exclude is True

def test_from_config_composite(filter_factory):
    config = {
        'type': 'composite',
        'filters': [
            {'type': 'difficulty', 'value': '>=medium'},
            {'type': 'tags', 'value': ['math']}
        ]
    }
    filter_instance = filter_factory.from_config(config)
    assert filter_instance.__class__.__name__ == 'CompositeFilter'
    assert len(filter_instance.filters) == 2

def test_from_cli_args_single(filter_factory):
    filter_instance = filter_factory.from_cli_args(difficulty='<=easy')
    assert filter_instance.__class__.__name__ == 'DifficultyFilter'
    assert filter_instance.value == 'easy'
    assert filter_instance.operator == '<='

def test_from_cli_args_multiple(filter_factory):
    filter_instance = filter_factory.from_cli_args(
        difficulty='>hard',
        tags=['science'],
        match_all_tags=True
    )
    assert filter_instance.__class__.__name__ == 'CompositeFilter'
    assert len(filter_instance.filters) == 2
