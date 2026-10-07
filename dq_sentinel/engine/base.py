"""
Defines DQDimensionBase, the parent class every DQ dimension inherits from.

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

    def execute(self, rule: str, series: pd.Series, **params) -> pd.Series:
        rule_method = getattr(self, rule, None)
        
        if rule_method is None or not callable(rule_method):
            raise AttributeError(
                f"'{rule}' is not implemented in the dimension '{self.__class__.__name__}'"
            )
        result = rule_method(series, **params)
        
        # Validate that the rule returned a pandas Series
        if not isinstance(result, pd.Series):
            raise TypeError(
                f"{self.__class__.__name__}.{rule} must return a boolean pandas Series, "
                f"got {type(result).__name__}"
            )

        # Validate that the Series contains boolean values.
        if result.dtype != bool:
            raise TypeError(
                f"{self.__class__.__name__}.{rule} must return a "
                f"boolean pandas Series, got dtype '{result.dtype}'"
            )
    
        return result