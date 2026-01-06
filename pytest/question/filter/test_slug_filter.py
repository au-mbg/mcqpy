
def test_slug_filter(slug_filter, question_set_with_meta):
    filtered_questions = slug_filter.apply(question_set_with_meta)
    slugs_in_filtered = [q.slug for q in filtered_questions]
    assert all(slug in slugs_in_filtered for slug in slug_filter.slugs)
    assert len(filtered_questions) == 2


