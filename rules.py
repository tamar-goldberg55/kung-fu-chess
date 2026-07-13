"""Board-format validation rules.

Important: these are *format* rules ("is this raw text well-formed?"),
not chess movement rules — movement rules do not exist yet in this
iteration. Keeping this separate from board.py and controller.py keeps
each module focused on a single responsibility (SRP).
"""

from typing import List


class BoardFormatError(ValueError):
    """Raised when raw board text violates the format contract."""


def validate_non_empty(rows: List[List[str]]) -> None:
    """A board fixture must contain at least one row."""
    if not rows:
        raise BoardFormatError("Board must contain at least one row")


def validate_rectangular(rows: List[List[str]]) -> None:
    """Every row must have the same number of cells."""
    widths = {len(row) for row in rows}
    if len(widths) > 1:
        raise BoardFormatError("All rows must have the same number of cells")
