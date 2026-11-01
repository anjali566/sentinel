import pandas as pd
from dq_sentinel.engine.base import DQDimensionBase


class Accuracy(DQDimensionBase):
    """
    Accuracy — checks whether values are correct in type or representation
    (e.g. a boolean-flag column actually contains only true/false values).
    """

    @staticmethod
    def is_boolean(values: pd.Series) -> pd.Series:
        """
        Check whether each value is a boolean.
        Returns a row-level boolean mask.
        """
        return values.apply(lambda value: isinstance(value, bool))
