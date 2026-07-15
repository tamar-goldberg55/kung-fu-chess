"""Tests for GameEngine, RuleEngine, and parallel motion."""

import io

import pytest

from board import Board
from game_engine import GameEngine
from piece import Piece
from rule_context import RuleContext
from rule_engine import RuleEngine
from text_test_runner import TextTestRunner


def test_rule_engine_rejects_friendly_destination():
    board = Board(3, 1)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(0, 2, Piece("w", "K"))
    engine = RuleEngine()
    context = RuleContext(board)
    result = engine.validate(context, 0, 0, 0, 2, board.get_piece(0, 0))
    assert result.allowed is False


def test_game_engine_request_move_rejects_when_game_over():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(0, 2, Piece("b", "K"))
    engine = GameEngine(board)
    engine.request_move(0, 0, 0, 2)
    engine.advance_time(1000)
    result = engine.request_move(0, 0, 0, 1)
    assert result.allowed is False
    assert result.reason == "game_over"


def test_parallel_moves_allowed():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(2, 2, Piece("b", "R"))
    engine = GameEngine(board)

    first = engine.request_move(0, 0, 0, 2)
    second = engine.request_move(2, 2, 2, 0)

    assert first.allowed is True
    assert second.allowed is True
    assert len(engine.arbiter.pending_motions) == 2


def test_active_motion_blocks_same_piece():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "R"))
    engine = GameEngine(board)
    engine.request_move(0, 0, 0, 2)
    result = engine.request_move(0, 0, 0, 1)
    assert result.allowed is False


def test_text_test_runner_print_board_command():
    input_data = (
        "Board:\n"
        "wK . .\n"
        "Commands:\n"
        "print board\n"
    )
    output = io.StringIO()
    TextTestRunner(io.StringIO(input_data), output).run()
    assert output.getvalue().strip() == "wK . ."


def test_pawn_forward_move():
    board = Board(3, 3)
    board.set_piece(1, 1, Piece("w", "P"))
    engine = GameEngine(board)
    result = engine.request_move(1, 1, 0, 1)
    assert result.allowed is True


def test_king_one_square_move():
    board = Board(3, 3)
    board.set_piece(1, 1, Piece("w", "K"))
    engine = GameEngine(board)
    result = engine.request_move(1, 1, 0, 0)
    assert result.allowed is True


def test_queen_diagonal_move():
    board = Board(4, 4)
    board.set_piece(0, 0, Piece("w", "Q"))
    engine = GameEngine(board)
    result = engine.request_move(0, 0, 3, 3)
    assert result.allowed is True
