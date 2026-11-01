import pandas as pd
import pytest

from dq_sentinel.rules.accuracy import Accuracy


@pytest.mark.parametrize(
    "values, expected",
    [
        ([True, False, True], [True, True, True]),
        ([True, "False", False], [True, False, True]),
        ([True, 1, 0, False], [True, False, False, True]),
        ([None, True, False], [False, True, True]),
        (["True", "False"], [False, False]),
    ],
)
def test_is_boolean(values, expected):
    series = pd.Series(values, dtype=object)

    result = Accuracy.is_boolean(series)

    expected_series = pd.Series(expected, dtype=bool)

    pd.testing.assert_series_equal(result, expected_series)