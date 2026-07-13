import pytest

from board import Board
from piece import Piece
from rules import is_legal_rook_move


def _rook(color):
    return Piece.from_token(f"{color}R")


def test_rook_moves_horizontally_on_an_empty_row():
    board = Board(3, 1)
    board.set_piece(0, 0, _rook("w"))
    assert is_legal_rook_move(board, 0, 0, 0, 2) is True


def test_rook_moves_vertically_on_an_empty_column():
    board = Board(1, 3)
    board.set_piece(0, 0, _rook("w"))
    assert is_legal_rook_move(board, 0, 0, 2, 0) is True


def test_rook_cannot_move_diagonally():
    board = Board(3, 3)
    board.set_piece(0, 0, _rook("w"))
    assert is_legal_rook_move(board, 0, 0, 2, 2) is False


def test_rook_is_blocked_by_a_friendly_piece_in_its_path():
    board = Board(3, 1)
    board.set_piece(0, 0, _rook("w"))
    board.set_piece(0, 1, _rook("w"))
    assert is_legal_rook_move(board, 0, 0, 0, 2) is False


def test_rook_can_capture_an_enemy_piece_at_the_end_of_a_clear_path():
    board = Board(3, 1)
    board.set_piece(0, 0, _rook("w"))
    board.set_piece(0, 2, _rook("b"))
    assert is_legal_rook_move(board, 0, 0, 0, 2) is True


def test_rook_cannot_pass_through_an_enemy_piece_to_reach_further():
    board = Board(4, 1)
    board.set_piece(0, 0, _rook("w"))
    board.set_piece(0, 1, _rook("b"))
    assert is_legal_rook_move(board, 0, 0, 0, 3) is False


def test_rook_blocked_going_upward_by_a_piece_along_the_way():
    board = Board(1, 3)
    board.set_piece(2, 0, _rook("w"))
    board.set_piece(1, 0, _rook("b"))
    assert is_legal_rook_move(board, 2, 0, 0, 0) is False


# @pytest.mark.xfail(
#     reason=(
#         "באג ידוע: is_legal_rook_move מחזיר True עבור תנועה מתא לעצמו, "
#         "בניגוד ל-is_legal_king_move שכן בודק את זה נכון. לא תוקן עדיין — "
#         "תיעוד מכוון לבאג, לא אישור שההתנהגות נכונה."
#     ),
#     strict=True,
# )
def test_rook_cannot_move_to_its_own_cell():
    board = Board(3, 3)
    board.set_piece(0, 0, _rook("w"))
    assert is_legal_rook_move(board, 0, 0, 0, 0) is False
