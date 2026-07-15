from piece_rules.base import PieceMoveRule
from piece_rules.bishop_rule import BishopRule
from piece_rules.rook_rule import RookRule
from rule_context import RuleContext


class QueenRule(PieceMoveRule):
    kind = "Q"

    def __init__(self):
        self._rook = RookRule()
        self._bishop = BishopRule()

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return self._rook.can_reach(from_row, from_col, to_row, to_col) or self._bishop.can_reach(
            from_row, from_col, to_row, to_col
        )

    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        if self._rook.can_reach(from_row, from_col, to_row, to_col):
            return self._rook._passes_board_constraints(context, from_row, from_col, to_row, to_col)
        return self._bishop._passes_board_constraints(context, from_row, from_col, to_row, to_col)
