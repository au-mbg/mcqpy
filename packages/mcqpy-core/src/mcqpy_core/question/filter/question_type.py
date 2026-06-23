"""Module for slug-based question filtering."""

from mcqpy_core.question.filter.base_filter import AttributeFilter

class TypeFilter(AttributeFilter):
    """Filter questions by type with exact match.
    
    Parameters
    ------------
    types: 
        Types to filter by
    """
    
    def __init__(self, types: list[str] | str):
        self.types = types if isinstance(types, list) else [types]
        super().__init__('question_type', self.types, self._type_predicate)
    
    def _type_predicate(self, question_type, _):
        return question_type in self.types