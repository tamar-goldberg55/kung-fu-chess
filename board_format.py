"""Board format validation for parsed text input."""

from typing import List


class BoardFormatError(ValueError):
    """Raised when raw board text violates the format contract."""


def validate_non_empty(rows: List[List[str]]) -> None:
    if not rows:
        raise BoardFormatError("Board must contain at least one row")


def validate_rectangular(rows: List[List[str]]) -> None:
    cleaned_rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    if not cleaned_rows:
        return
    widths = {len(row) for row in cleaned_rows}
    if len(widths) > 1:
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")
