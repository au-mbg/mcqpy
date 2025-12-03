

def test_tag_filter(tag_filter, question_set_with_meta):
    filtered_questions = tag_filter.apply(question_set_with_meta)
    if tag_filter.exclude:
        assert all('math' not in q.tags for q in filtered_questions)
    else:
        assert all('math' in q.tags for q in filtered_questions)

def test_tag_match_all_filter(tag_match_all_filter, question_set_with_meta):
    filtered_questions = tag_match_all_filter.apply(question_set_with_meta)
    if tag_match_all_filter.exclude:
        assert all(not all(tag in q.tags for tag in ['math', 'algebra']) for q in filtered_questions)
    else:
        assert all(all(tag in q.tags for tag in ['math', 'algebra']) for q in filtered_questions)

