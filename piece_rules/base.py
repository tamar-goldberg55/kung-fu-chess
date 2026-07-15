"""Base class for piece movement rules (Strategy Pattern)."""

from abc import ABC, abstractmethod

from rule_context import RuleContext


class PieceMoveRule(ABC):
    """Evaluates whether a piece may move from source to destination."""

    kind: str

    def is_legal(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        if from_row == to_row and from_col == to_col:
            return False
        if not self.can_reach(from_row, from_col, to_row, to_col):
            return False
        piece = context.get_piece(from_row, from_col)
        if piece is None:
            return False
        if not context.is_destination_allowed(to_row, to_col, piece.color):
            return False
        return self._passes_board_constraints(context, from_row, from_col, to_row, to_col)

    @abstractmethod
    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Theoretical movement shape without board obstructions."""

    @abstractmethod
    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        """Whether the path is clear given current board and pending targets."""
