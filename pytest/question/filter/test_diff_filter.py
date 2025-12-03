def test_difficulty_filter(difficulty_filter, question_set_with_meta):
    filtered_questions = difficulty_filter.apply(question_set_with_meta)
    assert all(q.difficulty == difficulty_filter.difficulty for q in filtered_questions)

def test_composite_tag_difficulty_filter(tag_filter, difficulty_filter, question_set_with_meta):
    composite_filter = tag_filter & difficulty_filter
    filtered_questions = composite_filter.apply(question_set_with_meta)
    for q in filtered_questions:
        if tag_filter.exclude:
            assert 'math' not in q.tags
        else:
            assert 'math' in q.tags
        assert q.difficulty == difficulty_filter.difficulty