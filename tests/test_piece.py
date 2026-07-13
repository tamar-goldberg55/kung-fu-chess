import pytest

from piece import InvalidPieceTokenError, Piece


def test_from_token_parses_color_and_kind():
    piece = Piece.from_token("wK")
    assert piece.color == "w"
    assert piece.kind == "K"


def test_from_token_black_piece():
    piece = Piece.from_token("bP")
    assert piece.color == "b"
    assert piece.kind == "P"


def test_to_token_round_trip():
    for token in ("wK", "bQ", "wR", "bN", "wB", "bP"):
        assert Piece.from_token(token).to_token() == token


@pytest.mark.parametrize("bad_token", ["", "w", "wKK", "wKw", "wKQ"])
def test_from_token_rejects_wrong_length(bad_token):
    with pytest.raises(InvalidPieceTokenError):
        Piece.from_token(bad_token)


def test_from_token_rejects_invalid_color():
    with pytest.raises(InvalidPieceTokenError):
        Piece.from_token("xK")


def test_from_token_rejects_invalid_kind():
    with pytest.raises(InvalidPieceTokenError):
        Piece.from_token("wZ")


def test_equal_pieces_are_equal():
    assert Piece.from_token("wK") == Piece.from_token("wK")


def test_different_color_pieces_are_not_equal():
    assert Piece.from_token("wK") != Piece.from_token("bK")


def test_different_kind_pieces_are_not_equal():
    assert Piece.from_token("wK") != Piece.from_token("wQ")


def test_piece_is_not_equal_to_non_piece():
    assert Piece.from_token("wK") != "wK"


def test_equal_pieces_have_equal_hash():
    assert hash(Piece.from_token("wK")) == hash(Piece.from_token("wK"))


def test_repr_contains_color_and_kind():
    representation = repr(Piece.from_token("wK"))
    assert "w" in representation and "K" in representation
