from board import Board
from piece import Piece
from rules import is_legal_bishop_move, is_legal_knight_move


def test_bishop_blocked_by_a_friendly_piece_in_its_path():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "B"))
    board.set_piece(1, 1, Piece("w", "P"))
    assert is_legal_bishop_move(board, 0, 0, 2, 2) is False


def test_bishop_can_capture_an_enemy_piece_at_the_end_of_a_clear_diagonal():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "B"))
    board.set_piece(2, 2, Piece("b", "P"))
    assert is_legal_bishop_move(board, 0, 0, 2, 2) is True


def test_knight_jumps_over_blocking_pieces():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "N"))
    board.set_piece(1, 0, Piece("w", "P"))  # חוסם ישירות מלפניו
    board.set_piece(0, 1, Piece("b", "R"))  # חוסם מהצד
    assert is_legal_knight_move(board, 0, 0, 2, 1) is True
