"""Tests for move log observer."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from board import GameEngine, Motion
from Grafic.default_board import create_standard_board
from Grafic.event_bridge import GfxEventBridge
from Grafic.observers.move_log_observer import MoveLogObserver
from Grafic.observers.score_observer import ScoreObserver
from Grafic.piece_state_manager import PieceStateManager
from piece import Piece


def test_move_log_records_immediately_on_schedule():
    board = create_standard_board()
    engine = GameEngine(board)
    piece_states = PieceStateManager(engine)
    score_observer = ScoreObserver()
    move_log = MoveLogObserver(board.height)
    bridge = GfxEventBridge(piece_states, score_observer, move_log)
    engine.add_listener(bridge)

    engine.request_move(6, 4, 4, 4)

    assert move_log.state.white_moves == [("0.0s", "Pawn: e2->e4")]


def test_move_log_splits_by_color():
    observer = MoveLogObserver(8)
    white_motion = Motion(Piece("w", "P"), 6, 0, 5, 0, 1000)
    black_motion = Motion(Piece("b", "P"), 1, 0, 2, 0, 1000)

    observer.on_move_scheduled(white_motion, 1200)
    observer.on_move_scheduled(black_motion, 3400)

    assert observer.state.white_moves[0][1] == "Pawn: a2->a3"
    assert observer.state.black_moves[0][0] == "3.4s"
