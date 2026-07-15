"""Textual board output."""

import sys
from typing import TextIO

from board import Board
from board_view import BoardViewAdapter


class PrintBoard:
    """Prints a board to a text stream using the View Adapter."""

    def __init__(self, output_stream: TextIO = sys.stdout):
        self._output = output_stream
        self._adapter = BoardViewAdapter()

    def print(self, board: Board) -> None:
        print(self._adapter.render(board), file=self._output)
