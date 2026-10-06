"""
Defines DQRuleBase, the parent class every DQ dimension inherits from.

Two responsibilities live here, and only these two:
  1. Self-registration — __init_subclass__ automatically adds every subclass
     to a shared registry, keyed by class name, the moment it's defined.
  2. Dynamic dispatch — execute() resolves a dq rule check by string name via
     getattr() and calls it, so the engine never hardcodes which dq check
     belongs to which class.
"""

import pandas as pd


class DQDimensionBase:
    registry = {} 

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        DQDimensionBase.registry[cls.__name__] = cls

    def execute(self, dq_rule: str, series: pd.Series, **params) -> pd.Series:
        rule = getattr(self, dq_rule, None)
        if rule is None or not callable(rule):
            raise AttributeError(
                f"'{dq_rule}' is not implemented in rule class '{self.__class__.__name__}'"
            )
        result = rule(series, **params)
        if not isinstance(result, pd.Series):
            raise TypeError(
                f"{self.__class__.__name__}.{dq_rule} must return a boolean pandas Series, "
                f"got {type(result).__name__}"
            )
        return result