"""Controller: orchestrates parsing raw fixture text into a Board, and
rendering a Board back into canonical text.

This module owns the *translation* between text and the model. It does
not talk to stdin/stdout directly (that belongs to main.py) and it does
not implement chess movement rules (that comes in a later iteration).
"""

from typing import List

from board import Board
from config import CELL_SEPARATOR, EMPTY_CELL
from piece import Piece
from rules import validate_non_empty, validate_rectangular


def _split_rows(text: str) -> List[List[str]]:
    """Split raw text into rows of whitespace-separated tokens.

    Blank/whitespace-only lines (e.g. a trailing newline) are ignored
    so they don't get counted as empty board rows.
    """
    lines = [line for line in text.splitlines() if line.strip() != ""]
    return [line.split() for line in lines]


def parse_board(text: str) -> Board:
    """Parse raw fixture text into a validated Board instance.

    Infers width/height from the text and validates:
      - at least one row exists
      - all rows have the same number of cells
      - every non-empty token is a legal piece token
    """
    raw_rows = _split_rows(text)
    validate_non_empty(raw_rows)
    validate_rectangular(raw_rows)

    height = len(raw_rows)
    width = len(raw_rows[0])
    board = Board(width, height)

    for row_index, row_tokens in enumerate(raw_rows):
        for col_index, token in enumerate(row_tokens):
            if token == EMPTY_CELL:
                continue
            board.set_piece(row_index, col_index, Piece.from_token(token))

    return board


def render_board(board: Board) -> str:
    """Render a Board back into its canonical textual form."""
    lines = []
    for row_index in range(board.height):
        tokens = []
        for col_index in range(board.width):
            piece = board.get_piece(row_index, col_index)
            tokens.append(piece.to_token() if piece else EMPTY_CELL)
        lines.append(CELL_SEPARATOR.join(tokens))
    return "\n".join(lines)
