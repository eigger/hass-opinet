"""api.py 단위 테스트."""
from custom_components.opinet.api import _strip_values


def test_strip_values_string():
    assert _strip_values("  test_string\r\n ") == "test_string"


def test_strip_values_list():
    assert _strip_values(["  a\r\n", " b "]) == ["a", "b"]


def test_strip_values_dict():
    assert _strip_values({"key1": "  val1\n", "key2": ["  val2  "]}) == {
        "key1": "val1",
        "key2": ["val2"],
    }
