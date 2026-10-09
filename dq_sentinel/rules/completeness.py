"""
Completeness — checks whether required data is present in a column
(nulls, blank strings). Assumes the column itself exists; whether the
column is present at all is a schema-conformance metric, computed in
DQProcessor, not here.
"""


import pandas as pd
from dq_sentinel.engine.base import DQDimensionBase

class Completeness(DQDimensionBase):
    
    @staticmethod
    def is_not_null(values):
        """Return a row mask that passes values that are not null."""
        return values.notna()

    @staticmethod
    def is_not_blank(values):
        """Return a row mask that passes non-null, non-blank values."""
        return values.notna() & values.astype("string").str.strip().ne("").fillna(False)