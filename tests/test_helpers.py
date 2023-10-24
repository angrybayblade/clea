"""Test helpers."""

from clea.helpers import get_function_metadata


def test_get_function_metadata_empty() -> None:
    """Test get_function_metadata method."""

    def _method_1() -> None:
        """Testing method 1."""

    defaults, type_mapping = get_function_metadata(_method_1)
    assert len(defaults) == 0
    assert len(type_mapping) == 1  # return param


def test_get_function_metadata_no_default() -> None:
    """Test get_function_metadata method."""

    def _method_1(name: int) -> None:
        """Testing method 1."""

    defaults, type_mapping = get_function_metadata(_method_1)
    assert defaults == {"name": None}
    assert len(type_mapping) == 2  # return param


def test_get_function_metadata_with_default() -> None:
    """Test get_function_metadata method."""

    def _method_1(name: int = 1) -> None:
        """Testing method 1."""

    defaults, type_mapping = get_function_metadata(_method_1)
    assert defaults == {"name": 1}
    assert len(type_mapping) == 2  # return param
