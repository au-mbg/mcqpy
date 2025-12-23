from mcqpy.question.filter.base_filter import BaseFilter, CompositeFilter
from mcqpy.question.filter.difficulty import DifficultyFilter
from mcqpy.question.filter.tag import TagFilter
from mcqpy.question.filter.date import DateFilter

class FilterFactory:
    """Creates filters from configuration dictionaries."""
    
    FILTER_MAP = {
        'difficulty': DifficultyFilter,
        'tag': TagFilter,
        'date': DateFilter,
    }
    
    @classmethod
    def from_config(cls, config: dict) -> BaseFilter:
        """Create filter from config dict.
        """
        filter_type = config.get('type')
        
        if filter_type == 'composite':
            filters = [cls.from_config(f) for f in config['filters']]
            return CompositeFilter(filters)
        
        filter_class = cls.FILTER_MAP.get(filter_type)
        if not filter_class:
            raise ValueError(f"Unknown filter type: {filter_type}")
            
        kwargs = {k: v for k, v in config.items() if k not in ['type']}        
        return filter_class(**kwargs)
    
    @classmethod
    def from_cli_args(cls, **kwargs) -> BaseFilter | None:
        """Create filter from CLI arguments."""
        filters = []
        
        if difficulty := kwargs.get('difficulty'):
            filters.append(DifficultyFilter(difficulty))
        
        if tags := kwargs.get('tags'):
            filters.append(TagFilter(tags, match_all=kwargs.get('match_all_tags', False)))
        
        if exclude_tags := kwargs.get('exclude_tags'):
            filters.append(TagFilter(exclude_tags, exclude=True))
        
        return CompositeFilter(filters) if len(filters) > 1 else filters[0] if filters else None