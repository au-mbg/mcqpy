"""Module for base-class for question filters."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable
import random

if TYPE_CHECKING:
    from mcqpy_core.question.question import Question

class BaseFilter(ABC):
    """Abstract base class for question filters."""
    
    @abstractmethod
    def apply(self, questions: list["Question"]) -> list["Question"]:
        raise NotImplementedError("Subclasses must implement this method.") # pragma: no cover
    
    def __and__(self, other: 'BaseFilter') -> 'CompositeFilter':
        """Allow chaining filters with & operator."""
        return CompositeFilter([self, other])
    
    def set_rng(self, rng: random.Random):
        """Set the random number generator for this filter and any sub-filters."""
        self._rng = rng

    def get_rng(self) -> random.Random:
        """Get the random number generator for this filter."""
        if hasattr(self, '_rng'):
            return self._rng
        return random.Random()  # Return a default RNG if not set


class CompositeFilter(BaseFilter):
    """Combines multiple filters into a single filter."""
    
    def __init__(self, filters: list[BaseFilter]):
        self.filters = filters
    
    def apply(self, questions: list["Question"]) -> list["Question"]:
        selected_questions = questions.copy()
        print(f"Applying CompositeFilter with {len(self.filters)} filters.")
        print(f"Initial number of questions: {len(selected_questions)}")
        for filt in self.filters:            
            selected_questions = filt.apply(selected_questions)
            print(f"After applying {filt.__class__.__name__}, number of questions: {len(selected_questions)}")

        return selected_questions
    
    def __and__(self, other: BaseFilter) -> 'CompositeFilter':
        return CompositeFilter(self.filters + [other])


class AttributeFilter(BaseFilter):
    """Generic filter based on question attributes."""
    
    def __init__(self, attribute: str, value: Any, predicate: Callable = None):
        self.attribute = attribute
        self.value = value
        self.predicate = predicate or (lambda q_val, v: q_val == v)
    
    def apply(self, questions: list["Question"]) -> list["Question"]:
        return [q for q in questions if self._matches(q)]
    
    def _matches(self, question: "Question") -> bool:
        q_value = getattr(question, self.attribute, None)
        return self.predicate(q_value, self.value)


__all__ = ['BaseFilter', 'CompositeFilter', 'AttributeFilter']
