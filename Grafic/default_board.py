"""Factory helpers for creating playable boards."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board import Board
from piece import Piece


def create_standard_board(width: int = 8, height: int = 8) -> Board:
    """Create a standard opening board. Defaults to 8x8."""
    board = Board(width, height)

    if width < 2 or height < 4:
        return board

    back_row = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for col in range(min(width, len(back_row))):
        board.set_piece(0, col, Piece("b", back_row[col]))
        board.set_piece(height - 1, col, Piece("w", back_row[col]))

    pawn_row_black = 1 if height > 1 else 0
    pawn_row_white = height - 2 if height > 2 else height - 1
    for col in range(width):
        board.set_piece(pawn_row_black, col, Piece("b", "P"))
        board.set_piece(pawn_row_white, col, Piece("w", "P"))

    return board
