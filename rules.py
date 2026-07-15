"""Board format validation, piece rules (Strategy), and RuleEngine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from board import Board, RuleContext, ValidationResult
from piece import Piece


class BoardFormatError(ValueError):
    """Raised when raw board text violates the format contract."""


def validate_non_empty(rows: List[List[str]]) -> None:
    if not rows:
        raise BoardFormatError("Board must contain at least one row")


def validate_rectangular(rows: List[List[str]]) -> None:
    cleaned_rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    if not cleaned_rows:
        return
    widths = {len(row) for row in cleaned_rows}
    if len(widths) > 1:
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")


class PieceMoveRule(ABC):
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
        ...

    @abstractmethod
    def _passes_board_constraints(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> bool:
        ...


class RookRule(PieceMoveRule):
    kind = "R"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return from_row == to_row or from_col == to_col

    def _passes_board_constraints(
        self, context, from_row, from_col, to_row, to_col
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


class BishopRule(PieceMoveRule):
    kind = "B"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return abs(to_row - from_row) == abs(to_col - from_col) and from_row != to_row

    def _passes_board_constraints(
        self, context, from_row, from_col, to_row, to_col
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


class KnightRule(PieceMoveRule):
    kind = "N"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _passes_board_constraints(
        self, context, from_row, from_col, to_row, to_col
    ) -> bool:
        return True


class KingRule(PieceMoveRule):
    kind = "K"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return row_diff <= 1 and col_diff <= 1

    def _passes_board_constraints(
        self, context, from_row, from_col, to_row, to_col
    ) -> bool:
        return True


class PawnRule(PieceMoveRule):
    kind = "P"

    def can_reach(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        return True

    def _passes_board_constraints(
        self, context, from_row, from_col, to_row, to_col
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
        self, context, from_row, from_col, to_row, to_col
    ) -> bool:
        if self._rook.can_reach(from_row, from_col, to_row, to_col):
            return self._rook._passes_board_constraints(context, from_row, from_col, to_row, to_col)
        return self._bishop._passes_board_constraints(context, from_row, from_col, to_row, to_col)


RULE_REGISTRY = {
    "R": RookRule(),
    "B": BishopRule(),
    "N": KnightRule(),
    "K": KingRule(),
    "P": PawnRule(),
    "Q": QueenRule(),
}


class RuleEngine:
    def validate(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        piece: Piece,
    ) -> ValidationResult:
        rule = RULE_REGISTRY.get(piece.kind)
        if rule is None:
            return ValidationResult(False, "unknown_piece_kind")
        if not rule.is_legal(context, from_row, from_col, to_row, to_col):
            return ValidationResult(False, "illegal_move")
        return ValidationResult(True)


def _validate_with_rule(board, rule_key, from_row, from_col, to_row, to_col):
    piece = board.get_piece(from_row, from_col)
    if piece is None:
        return False
    rule = RULE_REGISTRY.get(rule_key)
    if rule is None:
        return False
    context = RuleContext(board, set())
    return rule.is_legal(context, from_row, from_col, to_row, to_col)


def is_legal_rook_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "R", from_row, from_col, to_row, to_col)


def is_legal_bishop_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "B", from_row, from_col, to_row, to_col)


def is_legal_knight_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "N", from_row, from_col, to_row, to_col)


def is_legal_king_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "K", from_row, from_col, to_row, to_col)


def is_legal_pawn_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "P", from_row, from_col, to_row, to_col)


def is_legal_queen_move(board, from_row, from_col, to_row, to_col):
    return _validate_with_rule(board, "Q", from_row, from_col, to_row, to_col)


MOVE_VALIDATORS = {
    "R": is_legal_rook_move,
    "B": is_legal_bishop_move,
    "N": is_legal_knight_move,
    "K": is_legal_king_move,
    "P": is_legal_pawn_move,
    "Q": is_legal_queen_move,
}
