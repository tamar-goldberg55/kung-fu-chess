from board import Board
from piece import Piece


def test_board_stores_dimensions():
    board = Board(width=4, height=3)
    assert board.width == 4
    assert board.height == 3


def test_new_board_cells_are_empty():
    board = Board(width=2, height=2)
    for row in range(2):
        for col in range(2):
            assert board.get_piece(row, col) is None


def test_set_piece_then_get_piece_returns_same_piece():
    board = Board(width=2, height=2)
    piece = Piece.from_token("wK")
    board.set_piece(0, 1, piece)
    assert board.get_piece(0, 1) is piece


def test_setting_one_cell_does_not_affect_neighbors():
    board = Board(width=2, height=2)
    board.set_piece(0, 0, Piece.from_token("wK"))
    assert board.get_piece(0, 1) is None
    assert board.get_piece(1, 0) is None
    assert board.get_piece(1, 1) is None
