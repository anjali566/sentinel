import pytest

from dq_sentinel.engine.base import DQDimensionBase
from dq_sentinel.engine.dimension_factory import DQDimensionFactory
from dq_sentinel.rules.completeness import Completeness


def test_factory_returns_correct_dimension_instance():
    dimension = DQDimensionFactory.get_dimension_instance("Completeness")
    print(dimension)

    assert isinstance(dimension, Completeness)


def test_factory_returns_instance_registered_in_registry():
    dimension = DQDimensionFactory.get_dimension_instance("Completeness")

    assert type(dimension) is DQDimensionBase.registry["Completeness"]


def test_factory_raises_error_for_unknown_dimension():
    with pytest.raises(ValueError, match="Unknown DQ Dimension class"):
        DQDimensionFactory.get_dimension_instance("UnknownDimension")