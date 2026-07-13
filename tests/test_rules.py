import pytest

from rules import BoardFormatError, validate_non_empty, validate_rectangular


def test_validate_non_empty_rejects_empty_list():
    with pytest.raises(BoardFormatError):
        validate_non_empty([])


def test_validate_non_empty_accepts_non_empty_list():
    validate_non_empty([["wK", "."]])  # should not raise


def test_validate_rectangular_accepts_uniform_rows():
    rows = [["wK", ".", "."], [".", "wR", "."], [".", ".", "bK"]]
    validate_rectangular(rows)  # should not raise


def test_validate_rectangular_rejects_ragged_rows():
    rows = [["wK", "."], [".", "wR", "."]]
    with pytest.raises(BoardFormatError):
        validate_rectangular(rows)


def test_validate_rectangular_accepts_single_row():
    validate_rectangular([["wK", ".", "bK"]])  # should not raise
