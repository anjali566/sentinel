import pandas as pd
import pytest

from dq_sentinel.rules.completeness import Completeness


@pytest.mark.parametrize(
    "values, expected",
    [
        ([1001, 1002, 1003], [True, True, True]),
        ([1001, None, 1003], [True, False, True]),
        ([None, None, None], [False, False, False]),
    ],
)
def test_is_not_null(values, expected):
    series = pd.Series(values)

    result = Completeness.is_not_null(series)

    expected_series = pd.Series(expected, dtype=bool)

    pd.testing.assert_series_equal(result, expected_series)


@pytest.mark.parametrize(
    "values, expected",
    [
        (["Anjali", "Rahul", "Priya"], [True, True, True]),
        (["Anjali", None, "Priya"], [True, False, True]),
        (["Anjali", "", "Priya"], [True, False, True]),
        (["Anjali", "   ", "Priya"], [True, False, True]),
        (["  Anjali  ", "Rahul", " Priya "], [True, True, True]),
        ([None, "", "   "], [False, False, False]),
    ],
)
def test_is_not_blank(values, expected):
    series = pd.Series(values)

    result = Completeness.is_not_blank(series)

    expected_series = pd.Series(expected, dtype=bool)

    pd.testing.assert_series_equal(result, expected_series)