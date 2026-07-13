import pytest

from controller import parse_board, render_board
from piece import InvalidPieceTokenError, Piece
from rules import BoardFormatError

SAMPLE_TEXT = "wK . . .\n. wR . .\n. . bN .\n. . . bK\n"


def test_parse_board_infers_dimensions():
    board = parse_board(SAMPLE_TEXT)
    assert board.width == 4
    assert board.height == 4


def test_parse_board_places_pieces_correctly():
    board = parse_board(SAMPLE_TEXT)
    assert board.get_piece(0, 0) == Piece.from_token("wK")
    assert board.get_piece(1, 1) == Piece.from_token("wR")
    assert board.get_piece(2, 2) == Piece.from_token("bN")
    assert board.get_piece(3, 3) == Piece.from_token("bK")


def test_parse_board_leaves_empty_cells_as_none():
    board = parse_board(SAMPLE_TEXT)
    assert board.get_piece(0, 1) is None


def test_parse_board_rejects_ragged_rows():
    with pytest.raises(BoardFormatError):
        parse_board("wK . .\n. . .\n. . . .\n")


def test_parse_board_rejects_empty_input():
    with pytest.raises(BoardFormatError):
        parse_board("")


def test_parse_board_rejects_invalid_piece_token():
    with pytest.raises(InvalidPieceTokenError):
        parse_board("wK . .\nzZ . .\n. . .\n")


def test_render_board_round_trips_sample_text():
    board = parse_board(SAMPLE_TEXT)
    assert render_board(board) == SAMPLE_TEXT.rstrip("\n")


def test_render_board_all_empty_board():
    board = parse_board(". .\n. .\n")
    assert render_board(board) == ". .\n. ."
