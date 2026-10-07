from dq_sentinel.engine.base import DQDimensionBase


def test_subclass_is_registered():
    class TestDimension(DQDimensionBase):
        pass

    assert "TestDimension" in DQDimensionBase.registry
    assert DQDimensionBase.registry["TestDimension"] is TestDimension