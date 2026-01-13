import pytest
import pandas as pd

from mcqpy.grade.utils import get_grade_dataframe

@pytest.fixture
def grade_df(graded_sets) -> pd.DataFrame:
    return get_grade_dataframe(graded_sets, sort_key="total_points")

def test_get_dataframe_not_empty(grade_df):
    assert not grade_df.empty

def test_get_dataframe_columns(grade_df):    
    assert "total_points" in grade_df.columns

def test_get_dataframe_sorted(grade_df):
    assert grade_df['total_points'].is_monotonic_increasing
