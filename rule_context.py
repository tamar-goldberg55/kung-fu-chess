"""Read-only context for move validation against board state."""

from typing import Optional, Set, Tuple

from board import Board
from piece import Piece


class RuleContext:
    """Wraps the board plus in-flight motion targets for rule evaluation."""

    def __init__(self, board: Board, pending_targets: Optional[Set[Tuple[int, int]]] = None):
        self.board = board
        self._pending_targets = pending_targets or set()

    @property
    def width(self) -> int:
        return self.board.width

    @property
    def height(self) -> int:
        return self.board.height

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self.board.get_piece(row, col)

    def is_target_occupied_by_pending(self, row: int, col: int) -> bool:
        return (row, col) in self._pending_targets

    def is_destination_allowed(self, to_row: int, to_col: int, piece_color: str) -> bool:
        target = self.get_piece(to_row, to_col)
        if target is None:
            return True
        return target.color != piece_color
