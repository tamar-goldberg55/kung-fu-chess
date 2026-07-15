"""Backward-compatible facade for board parsing and rendering."""

from board_parser import parse_board
from board_view import BoardViewAdapter

_adapter = BoardViewAdapter()


def render_board(board):
    return _adapter.render(board)
