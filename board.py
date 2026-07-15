"""Pure board model — no rendering, no game engine logic."""

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
