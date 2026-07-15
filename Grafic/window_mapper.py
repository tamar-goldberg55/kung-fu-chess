"""Maps image pixel coordinates to board cells inside the rendered canvas."""

from __future__ import annotations

from typing import Tuple

from board_mapper import InvalidCoordinatesError
from Grafic.grafic_config import CELL_SIZE, HEADER_HEIGHT, SIDE_PANEL_WIDTH


class WindowMapper:
    """Converts image pixel coordinates into board row/col indices."""

    def __init__(
        self,
        board_width: int,
        board_height: int,
        board_offset_x: int = SIDE_PANEL_WIDTH,
        board_offset_y: int = HEADER_HEIGHT,
        cell_size: int = CELL_SIZE,
    ):
        self._board_width = board_width
        self._board_height = board_height
        self._board_offset_x = board_offset_x
        self._board_offset_y = board_offset_y
        self._cell_size = cell_size

    def to_cell(self, image_x: int, image_y: int) -> Tuple[int, int]:
        """Convert image pixel coordinates to board row/col."""
        board_x = image_x - self._board_offset_x
        board_y = image_y - self._board_offset_y

        if board_x < 0 or board_y < 0:
            raise InvalidCoordinatesError(f"Click outside board: ({image_x}, {image_y})")

        max_width_px = self._board_width * self._cell_size
        max_height_px = self._board_height * self._cell_size
        if board_x >= max_width_px or board_y >= max_height_px:
            raise InvalidCoordinatesError(f"Click outside board: ({image_x}, {image_y})")

        col = board_x // self._cell_size
        row = board_y // self._cell_size
        return row, col

    def cell_to_image_pixel(self, row: int, col: int) -> Tuple[int, int]:
        """Return the top-left image pixel for a board cell."""
        x = self._board_offset_x + col * self._cell_size
        y = self._board_offset_y + row * self._cell_size
        return x, y
