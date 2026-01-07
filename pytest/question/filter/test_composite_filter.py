from mcqpy.question.filter import CompositeFilter

def test_base_and_operator(tag_filter, difficulty_filter):
    composite_filter = tag_filter & difficulty_filter
    assert isinstance(composite_filter, CompositeFilter)
    assert len(composite_filter.filters) == 2

def test_composite_and_operator(tag_filter, difficulty_filter):
    composite_filter1 = tag_filter & difficulty_filter
    another_tag_filter = tag_filter
    composite_filter2 = composite_filter1 & another_tag_filter
    assert isinstance(composite_filter2, CompositeFilter)
    assert len(composite_filter2.filters) == 3