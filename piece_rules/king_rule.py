from piece_rules.base import PieceMoveRule
from rule_context import RuleContext


class KingRule(PieceMoveRule):
    kind = "K"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return row_diff <= 1 and col_diff <= 1

    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        return True
