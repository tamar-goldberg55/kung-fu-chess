"""Compute cell-by-cell paths for discrete Kung Fu Chess movement."""

from __future__ import annotations

from typing import List, Tuple


def motion_path_cells(
    piece_kind: str,
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
) -> List[Tuple[int, int]]:
    """Return every cell a piece occupies while traveling, including start."""
    cells = [(from_row, from_col)]
    if (from_row, from_col) == (to_row, to_col):
        return cells

    if piece_kind == "N":
        cells.append((to_row, to_col))
        return cells

    row_step = 0 if to_row == from_row else (1 if to_row > from_row else -1)
    col_step = 0 if to_col == from_col else (1 if to_col > from_col else -1)
    curr_row, curr_col = from_row + row_step, from_col + col_step
    while (curr_row, curr_col) != (to_row, to_col):
        cells.append((curr_row, curr_col))
        curr_row += row_step
        curr_col += col_step
    cells.append((to_row, to_col))
    return cells


def one_square_before(
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
) -> Tuple[int, int]:
    """Return the last free cell before the destination along a straight/diagonal line."""
    row_step = 0 if to_row == from_row else (1 if to_row > from_row else -1)
    col_step = 0 if to_col == from_col else (1 if to_col > from_col else -1)
    prev_row, prev_col = from_row, from_col
    curr_row, curr_col = from_row + row_step, from_col + col_step
    while (curr_row, curr_col) != (to_row, to_col):
        prev_row, prev_col = curr_row, curr_col
        curr_row += row_step
        curr_col += col_step
    return prev_row, prev_col


def current_path_index(path: List[Tuple[int, int]], elapsed_ms: int, step_ms: int) -> int:
    """Map elapsed travel time to the occupied path index."""
    if elapsed_ms <= 0 or len(path) <= 1:
        return 0
    max_index = len(path) - 1
    return min(max_index, elapsed_ms // step_ms)
