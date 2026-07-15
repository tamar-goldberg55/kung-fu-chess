from piece_rules.base import PieceMoveRule
from rule_context import RuleContext


class RookRule(PieceMoveRule):
    kind = "R"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return from_row == to_row or from_col == to_col

    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        step_r = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        step_c = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        curr_r, curr_c = from_row + step_r, from_col + step_c
        while curr_r != to_row or curr_c != to_col:
            if context.get_piece(curr_r, curr_c) is not None:
                return False
            if context.is_target_occupied_by_pending(curr_r, curr_c):
                return False
            curr_r += step_r
            curr_c += step_c
        return True
