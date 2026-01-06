import pytest
from mcqpy.question.utils import _norm_caps, _norm_images, _norm_opts


def test_norm_images_list_error():
    with pytest.raises(TypeError):
        _norm_images([1, 'str'])

def test_norm_images_type_error():
    with pytest.raises(TypeError):
        _norm_images(123)

def test_norm_opts_type_error():
    with pytest.raises(TypeError):
        _norm_opts(['not', 'a', 'dict'])

def test_norm_opts_indexed_type_error():
    with pytest.raises(TypeError):
        _norm_opts({0: ['not', 'a', 'dict']})

def test_norm_opts_indexed_value_error():
    with pytest.raises(ValueError):
        _norm_opts({0: {'key': ['not', 'a', 'scalar']}})

def test_norm_opts_not_scalar_error():
    class DummyType:
        pass
    with pytest.raises(ValueError):
        _norm_opts({'k': 'v', 'j':DummyType()})

def test_norm_opts_mixed_keys_error():
    with pytest.raises(ValueError):
        _norm_opts({0: {'key': 'value'}, '1': {'key': 'value'}})

def test_norm_caps_value_error():
    with pytest.raises(TypeError):
        _norm_caps({0: 123})   

def test_norm_caps_mixed_keys_error():
    with pytest.raises(TypeError):
        _norm_caps({0: 'caption', '1': 'another caption'})

def test_norm_caps_type_error():
    with pytest.raises(TypeError):
        _norm_caps(['not', 'a', 'dict'])