from mcqpy.question.filter.date import DateFilter
from datetime import date
from dataclasses import dataclass

@dataclass
class MockQuestion:
    created_date: str

def test_date_filter(date_filter, question_set_with_meta):
    filtered_questions = date_filter.apply(question_set_with_meta)
    for q in filtered_questions:
        assert q.created_date == "01/01/2025"

def test_date_filter_operator(date_filter):
    operator, date_value = date_filter._parse_date_operator('>=15/03/2024')
    assert operator == '>='
    assert date_value == '15/03/2024'

def test_date_filter_parse_range(date_filter):
    start_date, end_date = date_filter._parse_date_range('2024')
    assert start_date == date(2024, 1, 1)
    assert end_date == date(2024, 12, 31)

def test_date_filter_matches(date_filter):
    date = '16/03/2024'
    date_filter.operator = '>'
    date_filter.start_date = date_filter._parse_date_range('15/03/2024')
    assert date_filter._matches_date(date) is True

def test_date_filter_not_matches(date_filter):
    date = '14/03/2024'
    date_filter.operator = '>'
    date_filter.start_date = date_filter._parse_date_range('15/03/2024')
    assert date_filter._matches_date(date) is False

def test_date_filter_less_than_matches(date_filter):
    date = '10/03/2024'
    date_filter.operator = '<'
    date_filter.start_date = date_filter._parse_date_range('15/03/2024')
    assert date_filter._matches_date(date) is True

def test_date_filter_range_matches(date_filter):
    date = '15/06/2024'
    date_filter.is_range = True
    date_filter.start_date = date_filter._parse_date_range('01/01/2024')
    date_filter.end_date = date_filter._parse_date_range('31/12/2024')
    assert date_filter._matches_date(date) is True

def test_date_filter_range_not_matches(date_filter):
    date = '15/06/2025'
    date_filter.is_range = True
    date_filter.start_date = date_filter._parse_date_range('01/01/2024')
    date_filter.end_date = date_filter._parse_date_range('31/12/2024')
    assert date_filter._matches_date(date) is False

def test_date_filter_apply(date_filter):

    date_filter.start_date = date_filter._parse_date_range('01/01/2024')
    date_filter.end_date = date_filter._parse_date_range('31/12/2024')
    date_filter.is_range = True

    questions = [
        MockQuestion(created_date='15/03/2024'),
        MockQuestion(created_date='20/05/2024'),
        MockQuestion(created_date='10/01/2025'),
        MockQuestion(created_date=None),
    ]

    date_filter.strict_missing = False
    date_filter.apply(questions)






