"""BoardMapper: Maps screen pixel coordinates to pure logical board coordinates."""

from typing import Tuple
from board import Board

CELL_SIZE = 100


class InvalidCoordinatesError(ValueError):
    """Raised when pixel clicks fall outside the legal boundaries of the board."""


class BoardMapper:
    """Adapts continuous pixel coordinates into discrete board row and column indices."""

    def __init__(self, board: Board):
        self._board = board

    def to_cell(self, x: int, y: int) -> Tuple[int, int]:
        """Convert pixel (x, y) coordinates to board index (row, col)."""
        if x < 0 or y < 0:
            raise InvalidCoordinatesError(f"Coordinates cannot be negative: ({x}, {y})")
            
        max_width_px = self._board.width * CELL_SIZE
        max_height_px = self._board.height * CELL_SIZE
        
        if x >= max_width_px or y >= max_height_px:
            raise InvalidCoordinatesError(f"Click out of bounds: ({x}, {y})")

        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        return row, col