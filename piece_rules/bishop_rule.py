from piece_rules.base import PieceMoveRule
from rule_context import RuleContext


class BishopRule(PieceMoveRule):
    kind = "B"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return abs(to_row - from_row) == abs(to_col - from_col) and from_row != to_row

    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        curr_r, curr_c = from_row + row_step, from_col + col_step
        while curr_r != to_row:
            if context.get_piece(curr_r, curr_c) is not None:
                return False
            if context.is_target_occupied_by_pending(curr_r, curr_c):
                return False
            curr_r += row_step
            curr_c += col_step
        return True
