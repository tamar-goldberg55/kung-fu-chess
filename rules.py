"""Backward-compatible re-exports for piece move validation."""

from board_format import BoardFormatError, validate_non_empty, validate_rectangular
from piece_rules import RULE_REGISTRY
from rule_context import RuleContext


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
