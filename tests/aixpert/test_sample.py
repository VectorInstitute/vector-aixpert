"""Sample test."""

import pytest

import src.aixpert


@pytest.mark.integration_test()
def test_import():
    assert hasattr(src.aixpert, "__name__")


# TODO: Replace this
def test_samplefn(my_test_number: int) -> None:
    """Test function."""
    assert my_test_number == 42
