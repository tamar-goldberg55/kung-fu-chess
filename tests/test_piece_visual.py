"""Tests for piece visual stepping during motion."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from board import GameEngine
from Grafic.default_board import create_standard_board
from Grafic.piece_state_manager import PieceStateManager


def test_piece_stays_on_start_square_until_next_cell():
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
    assert tracked.visual_row == 6.0
    assert tracked.visual_col == 4.0


def test_piece_advances_one_square_per_move_duration():
    board = create_standard_board()
    engine = GameEngine(board)
    piece_states = PieceStateManager(engine)

    engine.request_move(6, 4, 4, 4)
    piece_states.on_move_requested(6, 4, 4, 4)
    engine.advance_time(1000)
    piece_states.update(1000)

    moving = [p for p in piece_states.pieces if p.state == "move"]
    assert len(moving) == 1
    assert moving[0].visual_row == 5.0
