"""Tests for piece visual smooth interpolation during motion."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from board import GameEngine
from Grafic.default_board import create_standard_board
from Grafic.piece_state_manager import PieceStateManager


def test_piece_visual_position_interpolates_smoothly_during_move():
    board = create_standard_board()
    engine = GameEngine(board)
    piece_states = PieceStateManager(engine)

    result = engine.request_move(6, 4, 4, 4)
    assert result.allowed

    piece_states.on_move_requested(6, 4, 4, 4)
    engine.advance_time(500)
    piece_states.update(500)

    moving = [p for p in piece_states.pieces if p.state == "move"]
    assert len(moving) == 1
    tracked = moving[0]
    assert 4.0 < tracked.visual_row < 6.0
    assert tracked.visual_col == 4.0


def test_piece_reaches_destination_after_full_travel_time():
    board = create_standard_board()
    engine = GameEngine(board)
    piece_states = PieceStateManager(engine)

    engine.request_move(6, 4, 4, 4)
    piece_states.on_move_requested(6, 4, 4, 4)
    engine.advance_time(1500)
    piece_states.update(1500)

    moving = [p for p in piece_states.pieces if p.state == "move"]
    assert len(moving) == 1
    assert moving[0].visual_row == 4.5
