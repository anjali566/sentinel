"""
DQDimensionFactory — resolves a rule class instance purely from its string name.

Given a class name from config (e.g. "Completeness"), looks it up in
DQDimensionBase.registry and returns a ready-to-use instance. The single point
of translation between "a string in a config file" and "a live Python
object" — nothing else in the codebase instantiates a rule class directly.
"""

from dq_sentinel.engine.base import DQDimensionBase


class DQDimensionFactory:
    @staticmethod
    def get_dimension_instance(dimension: str):
        dimension_cls = DQDimensionBase.registry.get(dimension)
        if dimension_cls is None:
            available = ", ".join(sorted(DQDimensionBase.registry.keys()))
            raise ValueError(
                f"Unknown DQ Dimension class: '{dimension}'. Available Dimensions: {available}"
            )
        return dimension_cls()