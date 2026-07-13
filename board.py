"""Board: the pure logical model of piece placement on a grid.

Board owns width, height, and cell occupancy only. It knows nothing
about text parsing, printing format, pixels, or movement rules — those
belong to controller.py, rules.py, and (in later iterations) the rules
engine and renderer.
"""

from typing import List, Optional

from piece import Piece


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cells: List[List[Optional[Piece]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        self._cells[row][col] = piece

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self._cells[row][col]
