from piece_rules.base import PieceMoveRule
from rule_context import RuleContext


class PawnRule(PieceMoveRule):
    kind = "P"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return True

    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        piece = context.get_piece(from_row, from_col)
        direction = -1 if piece.color == "w" else 1
        start_row = context.height - 1 if piece.color == "w" else 0

        if from_col == to_col and to_row == from_row + direction:
            is_static_free = context.get_piece(to_row, to_col) is None
            is_pending_free = not context.is_target_occupied_by_pending(to_row, to_col)
            return is_static_free and is_pending_free

        if from_col == to_col and from_row == start_row and to_row == from_row + 2 * direction:
            mid_row = from_row + direction
            mid_clear = (
                context.get_piece(mid_row, to_col) is None
                and not context.is_target_occupied_by_pending(mid_row, to_col)
            )
            dest_clear = (
                context.get_piece(to_row, to_col) is None
                and not context.is_target_occupied_by_pending(to_row, to_col)
            )
            return mid_clear and dest_clear

        if abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target = context.get_piece(to_row, to_col)
            return target is not None and target.color != piece.color

        return False
