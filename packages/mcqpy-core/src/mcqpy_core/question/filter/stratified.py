"""
Module for stratified question filtering.
"""
from typing import TYPE_CHECKING
from mcqpy_core.question.filter.base_filter import BaseFilter

if TYPE_CHECKING:
    from mcqpy_core.question.question import Question


class StratifiedFilter(BaseFilter):
    """
    Stratified selection filter
    """
    def __init__(
        self,
        number_of_questions: int,
        filters: list[BaseFilter] | None = None,
        proportions: list[float] | None = None,
        filter_configs: list[dict] | None = None,
    ):

        """
        Stratified filter to select questions based on multiple filters and specified proportions.

        Parameters
        ------------
        number_of_questions: 
            Total number of questions to select.
        filters: 
            List of BaseFilter instances to apply.
        proportions: 
            List of proportions corresponding to each filter.
        filter_configs: 
            List of filter configuration dictionaries to create filters if `filters` is None.
        """        


        if filters is None:
            if filter_configs is None:
                raise ValueError("Either filters or filter_configs must be provided.")
            filters = self._make_filters(filter_configs)
        
        if proportions is None:
            proportions = [1.0 / len(filters)] * len(filters)
        
        if len(filters) != len(proportions):
            raise ValueError("Length of filters and proportions must match.")
        else: # Normalize        
            total = sum(proportions)
            proportions = [p / total for p in proportions]

        self.filters = filters
        self.proportions = proportions
        self.number_of_questions = number_of_questions

    def apply(self, questions: list["Question"]) -> list["Question"]:
        total_questions = self.number_of_questions
        rng = self.get_rng()

        remaining_questions = []
        selected_questions = []

        # Apply each filter        
        for filt, prop in zip(self.filters, self.proportions):
            num_to_select = int(total_questions * prop)
            filtered = list(filt.apply(questions))
            rng.shuffle(filtered)
            selected, remaining = filtered[:num_to_select], filtered[num_to_select:]
            selected_questions.extend(selected)
            remaining_questions.extend(remaining)

        # If we have fewer than the desired number of questions, fill in from the remaining pool
        if len(selected_questions) < total_questions:
            rng.shuffle(remaining_questions)
            selected_questions.extend(remaining_questions[:total_questions - len(selected_questions)])
        
        return selected_questions
    
    def _make_filters(self, filter_configs: list[dict]) -> list[BaseFilter]:
        from mcqpy_core.question.filter import FilterFactory
        return [FilterFactory.from_config(cfg) for cfg in filter_configs]
