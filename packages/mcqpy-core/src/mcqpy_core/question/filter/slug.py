"""Module for slug-based question filtering."""

from mcqpy_core.question.filter.base_filter import AttributeFilter

class SlugFilter(AttributeFilter):
    """Filter questions by slug with exact match.
    
    Parameters
    ------------
    slugs: 
        Slugs to filter by
    """
    
    def __init__(self, slugs: list[str] | str):
        self.slugs = slugs if isinstance(slugs, list) else [slugs]
        super().__init__('slug', self.slugs, self._slug_predicate)
    
    def _slug_predicate(self, question_slug, _):
        return question_slug in self.slugs