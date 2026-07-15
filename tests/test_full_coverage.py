"""Tests targeting remaining uncovered lines for full code coverage."""

import io
import runpy
from unittest.mock import patch

import pytest

from board import Board
from board_format import validate_rectangular
from board_parser import _split_rows
from game_controller import GameController
from game_engine import GameEngine
from motion import Motion
from piece import Piece
from piece_rules.bishop_rule import BishopRule
from piece_rules.pawn_rule import PawnRule
from piece_rules.queen_rule import QueenRule
from piece_rules.rook_rule import RookRule
from real_time_arbiter import RealTimeArbiter
from motion import Motion
from rule_context import RuleContext
from rule_engine import RuleEngine
from rules import (
    is_legal_king_move,
    is_legal_pawn_move,
    is_legal_queen_move,
    _validate_with_rule,
)
from text_test_runner import TextTestRunner


def test_validate_rectangular_ignores_all_blank_rows():
    validate_rectangular([[], ["  ", "  "]])


def test_split_rows_skips_blank_lines_inside_board_section():
    text = "Board:\nwK . .\n\n. . .\nCommands:\nclick 0 0\n"
    rows = _split_rows(text)
    assert rows == [["wK", ".", "."], [".", ".", "."]]


def test_rule_context_width_property():
    board = Board(5, 4)
    context = RuleContext(board)
    assert context.width == 5
    assert context.height == 4


def test_rule_engine_unknown_piece_kind():
    engine = RuleEngine()
    board = Board(2, 2)
    fake = Piece("w", "K")
    fake.kind = "Z"
    result = engine.validate(RuleContext(board), 0, 0, 1, 1, fake)
    assert result.allowed is False
    assert result.reason == "unknown_piece_kind"


def test_rook_rule_blocked_by_pending_target_on_path():
    board = Board(3, 1)
    board.set_piece(0, 0, Piece("w", "R"))
    context = RuleContext(board, pending_targets={(0, 1)})
    rule = RookRule()
    assert rule.is_legal(context, 0, 0, 0, 2) is False


def test_bishop_rule_blocked_by_pending_target_on_path():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "B"))
    context = RuleContext(board, pending_targets={(1, 1)})
    assert BishopRule().is_legal(context, 0, 0, 2, 2) is False


def test_rook_rule_no_piece_at_source():
    board = Board(3, 3)
    context = RuleContext(board)
    assert RookRule().is_legal(context, 0, 0, 1, 0) is False


def test_pawn_double_step_from_start_row():
    board = Board(8, 8)
    board.set_piece(6, 4, Piece("w", "P"))
    context = RuleContext(board)
    rule = PawnRule()
    assert rule.is_legal(context, 6, 4, 4, 4) is True


def test_pawn_diagonal_capture():
    board = Board(8, 8)
    board.set_piece(6, 4, Piece("w", "P"))
    board.set_piece(5, 5, Piece("b", "P"))
    context = RuleContext(board)
    assert PawnRule().is_legal(context, 6, 4, 5, 5) is True


def test_pawn_invalid_move_returns_false():
    board = Board(8, 8)
    board.set_piece(6, 4, Piece("w", "P"))
    context = RuleContext(board)
    assert PawnRule().is_legal(context, 6, 4, 6, 5) is False


def test_pawn_black_double_step():
    board = Board(8, 8)
    board.set_piece(1, 4, Piece("b", "P"))
    context = RuleContext(board)
    assert PawnRule().is_legal(context, 1, 4, 3, 4) is True


def test_queen_horizontal_move_uses_rook_path():
    board = Board(4, 1)
    board.set_piece(0, 0, Piece("w", "Q"))
    context = RuleContext(board)
    assert QueenRule().is_legal(context, 0, 0, 0, 3) is True


def test_game_engine_current_time_and_no_piece():
    board = Board(2, 2)
    engine = GameEngine(board)
    assert engine.current_time == 0
    result = engine.request_move(0, 0, 1, 1)
    assert result.allowed is False
    assert result.reason == "no_piece_at_source"


def test_game_engine_piece_already_moving_branch():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "R"))
    engine = GameEngine(board)
    with patch.object(engine.arbiter, "has_active_motion_for", return_value=False):
        with patch.object(engine.arbiter, "is_piece_moving", return_value=True):
            result = engine.request_move(0, 0, 0, 2)
    assert result.allowed is False
    assert result.reason == "piece_already_moving"


def test_game_engine_request_jump_and_game_over():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "K"))
    engine = GameEngine(board)
    assert engine.request_jump(0, 0) is True
    assert engine.request_jump(1, 1) is False

    board.set_piece(0, 1, Piece("b", "K"))
    engine.request_move(0, 0, 0, 1)
    engine.advance_time(1000)
    assert engine.request_jump(0, 0) is False


def test_game_engine_black_pawn_promotion():
    board = Board(3, 3)
    board.set_piece(1, 1, Piece("b", "P"))
    engine = GameEngine(board)
    engine.request_move(1, 1, 2, 1)
    engine.advance_time(1000)
    assert board.get_piece(2, 1) == Piece("b", "Q")


def test_game_engine_active_motion_conflict_on_target():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(2, 0, Piece("w", "N"))
    engine = GameEngine(board)
    engine.request_move(0, 0, 0, 2)
    result = engine.request_move(2, 0, 0, 2)
    assert result.allowed is False
    assert result.reason == "friendly_destination_conflict"


def test_real_time_arbiter_has_no_conflict_when_unrelated():
    arbiter = RealTimeArbiter()
    arbiter.schedule_motion(
        Motion(Piece("w", "R"), 0, 0, 0, 2, arrival_time=100)
    )
    assert arbiter.has_active_motion_for(1, 1, 1, 2) is False


def test_real_time_arbiter_jump_failures():
    arbiter = RealTimeArbiter()
    board = Board(2, 2)
    assert arbiter.start_jump(board, 0, 0, 0) is False

    board.set_piece(0, 0, Piece("w", "K"))
    assert arbiter.start_jump(board, 0, 0, 0) is True
    assert arbiter.start_jump(board, 0, 0, 0) is False

    arbiter.airborne_pieces.clear()
    arbiter.schedule_motion(
        Motion(Piece("w", "K"), 0, 0, 0, 1, arrival_time=100)
    )
    assert arbiter.start_jump(board, 0, 0, 0) is False


def test_real_time_arbiter_force_all():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "R"))
    arbiter = RealTimeArbiter()
    captured = []
    promoted = []

    arbiter.schedule_motion(
        Motion(Piece("w", "R"), 0, 0, 0, 1, arrival_time=100)
    )
    arbiter.force_all(board, captured.append, lambda r, c: promoted.append((r, c)))
    assert board.get_piece(0, 1) == Piece("w", "R")
    assert board.get_piece(0, 0) is None


def test_real_time_arbiter_airborne_interception():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(0, 1, Piece("b", "N"))
    arbiter = RealTimeArbiter()
    arbiter.airborne_pieces.append(
        {"piece": Piece("b", "N"), "row": 0, "col": 1, "land_time": 500}
    )
    motion = Motion(Piece("w", "R"), 0, 0, 0, 1, arrival_time=100)
    arbiter._apply_motion(board, motion, lambda p: None, lambda r, c: None)
    assert board.get_piece(0, 0) is None
    assert board.get_piece(0, 1) == Piece("b", "N")


def test_real_time_arbiter_skips_friendly_destination():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "R"))
    board.set_piece(0, 1, Piece("w", "K"))
    arbiter = RealTimeArbiter()
    motion = Motion(Piece("w", "R"), 0, 0, 0, 1, arrival_time=100)
    arbiter._apply_motion(board, motion, lambda p: None, lambda r, c: None)
    assert board.get_piece(0, 0) == Piece("w", "R")
    assert board.get_piece(0, 1) == Piece("w", "K")


def test_game_controller_clears_selection_on_illegal_move():
    board = Board(3, 3)
    board.set_piece(0, 0, Piece("w", "K"))
    controller = GameController(GameEngine(board))
    controller.handle_click(50, 50)
    controller.handle_click(250, 250)
    assert controller._selected_piece is None


def test_game_controller_ignores_input_after_game_over():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "K"))
    board.set_piece(0, 1, Piece("b", "K"))
    engine = GameEngine(board)
    controller = GameController(engine)
    engine.request_move(0, 0, 0, 1)
    engine.advance_time(1000)
    assert engine.game_over is True
    controller.handle_click(50, 50)
    controller.handle_jump(50, 50)


def test_game_controller_jump_invalid_coordinates():
    board = Board(2, 2)
    board.set_piece(0, 0, Piece("w", "K"))
    controller = GameController(GameEngine(board))
    controller.handle_jump(-1, 0)


def test_text_test_runner_jump_command():
    input_data = (
        "Board:\n"
        "wK . .\n"
        "Commands:\n"
        "jump 50 50\n"
        "print board\n"
    )
    output = io.StringIO()
    TextTestRunner(io.StringIO(input_data), output).run()
    assert "wK" in output.getvalue()


def test_rules_compat_wrappers_and_edge_cases():
    board = Board(8, 8)
    assert _validate_with_rule(board, "R", 0, 0, 1, 1) is False

    board.set_piece(0, 0, Piece("w", "R"))
    assert _validate_with_rule(board, "Z", 0, 0, 1, 1) is False

    king_board = Board(3, 3)
    king_board.set_piece(1, 1, Piece("w", "K"))
    assert is_legal_king_move(king_board, 1, 1, 0, 0) is True

    pawn_board = Board(8, 8)
    pawn_board.set_piece(6, 4, Piece("w", "P"))
    assert is_legal_pawn_move(pawn_board, 6, 4, 5, 4) is True

    queen_board = Board(3, 1)
    queen_board.set_piece(0, 0, Piece("w", "Q"))
    assert is_legal_queen_move(queen_board, 0, 0, 0, 2) is True


def test_knight_move_duration_is_three_seconds():
    from board import move_duration_ms
    assert move_duration_ms("N", 0, 0, 2, 1) == 3000


def test_apply_motion_skips_when_source_piece_gone():
    board = Board(2, 1)
    board.set_piece(0, 0, Piece("w", "R"))
    arbiter = RealTimeArbiter()
    motion = Motion(Piece("w", "R"), 0, 0, 0, 1, arrival_time=100)
    board.set_piece(0, 0, None)
    arbiter._apply_motion(board, motion, lambda p: None, lambda r, c: None)
    assert board.get_piece(0, 1) is None


def test_main_module_entry_point():
    with patch("sys.stdin", io.StringIO(". .\n. .\n")), patch("sys.stdout", io.StringIO()):
        runpy.run_module("main", run_name="__main__")
