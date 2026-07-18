"""Tests for jump when threatened by capture."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from board import Board, GameEngine
from Grafic.default_board import create_standard_board
from Grafic.grafic_config import CELL_SIZE, DOUBLE_CLICK_MS, HEADER_HEIGHT, SIDE_PANEL_WIDTH
from Grafic.gui_main import GuiApp
from Grafic.threat_detection import is_threatened_by_capture
from piece import Piece


def _cell_center(row: int, col: int) -> tuple[int, int]:
    x = SIDE_PANEL_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
    y = HEADER_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def test_threatened_piece_detected_when_enemy_heads_to_capture():
    board = Board(8, 8)
    board.set_piece(6, 3, Piece("w", "P"))
    board.set_piece(5, 4, Piece("b", "P"))
    engine = GameEngine(board)
    engine.request_move(6, 3, 5, 4)

    assert is_threatened_by_capture(engine, 5, 4) is True
    assert is_threatened_by_capture(engine, 6, 3) is False


def test_double_click_jump_on_threatened_piece_without_prior_selection():
    board = Board(8, 8)
    board.set_piece(6, 3, Piece("w", "P"))
    board.set_piece(5, 4, Piece("b", "P"))
    app = GuiApp(board)

    app.controller.handle_click(*_cell_center(6, 3), 1000)
    app.controller.handle_click(*_cell_center(5, 4), 1500)

    app.controller.handle_click(*_cell_center(5, 4), 2000)
    app.controller.handle_click(*_cell_center(5, 4), 2000 + DOUBLE_CLICK_MS - 50)

    assert len(app.engine.arbiter.airborne_pieces) == 1
    assert "jump" in app.controller.status_message.lower() or "avoided" in app.controller.status_message.lower()


def test_jump_prevents_capture_on_arrival():
    board = Board(8, 8)
    board.set_piece(6, 3, Piece("w", "P"))
    board.set_piece(5, 4, Piece("b", "P"))
    engine = GameEngine(board)
    engine.request_move(6, 3, 5, 4)
    engine.request_jump(5, 4)

    engine.advance_time(1000)

    assert board.get_piece(5, 4) == Piece("b", "P")
    assert board.get_piece(6, 3) is None
