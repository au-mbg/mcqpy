from abc import ABC, abstractmethod
from mcqpy.question import Question
from typing import Any, Callable

class BaseFilter(ABC):
    """Abstract base class for question filters."""
    
    @abstractmethod
    def apply(self, questions: list[Question]) -> list[Question]:
        raise NotImplementedError("Subclasses must implement this method.")
    
    def __and__(self, other: 'BaseFilter') -> 'CompositeFilter':
        """Allow chaining filters with & operator."""
        return CompositeFilter([self, other])


class CompositeFilter(BaseFilter):
    """Combines multiple filters into a single filter."""
    
    def __init__(self, filters: list[BaseFilter]):
        self.filters = filters
    
    def apply(self, questions: list[Question]) -> list[Question]:
        result = questions
        for filter_obj in self.filters:
            result = filter_obj.apply(result)
        return result
    
    def __and__(self, other: BaseFilter) -> 'CompositeFilter':
        return CompositeFilter(self.filters + [other])


class AttributeFilter(BaseFilter):
    """Generic filter based on question attributes."""
    
    def __init__(self, attribute: str, value: Any, predicate: Callable = None):
        self.attribute = attribute
        self.value = value
        self.predicate = predicate or (lambda q_val, v: q_val == v)
    
    def apply(self, questions: list[Question]) -> list[Question]:
        return [q for q in questions if self._matches(q)]
    
    def _matches(self, question: Question) -> bool:
        q_value = getattr(question, self.attribute, None)
        return self.predicate(q_value, self.value)


__all__ = ['BaseFilter', 'CompositeFilter', 'AttributeFilter']