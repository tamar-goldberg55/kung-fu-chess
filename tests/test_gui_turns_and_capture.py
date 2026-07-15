"""Tests for parallel play, capture clicks, and captured-piece visuals."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from board import Board, GameEngine
from Grafic.default_board import create_standard_board
from Grafic.grafic_config import CELL_SIZE, HEADER_HEIGHT, SIDE_PANEL_WIDTH
from Grafic.gui_main import GuiApp
from piece import Piece


def _cell_center(row: int, col: int) -> tuple[int, int]:
    x = SIDE_PANEL_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
    y = HEADER_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def test_capture_via_selected_piece_and_green_square():
    board = Board(8, 8)
    board.set_piece(6, 3, Piece("w", "P"))
    board.set_piece(5, 4, Piece("b", "P"))
    app = GuiApp(board)

    app.controller.handle_click(*_cell_center(6, 3), 1000)
    assert app.controller.selected_pos == (6, 3)
    assert (5, 4) in app.controller.legal_moves

    app.controller.handle_click(*_cell_center(5, 4), 2000)
    assert len(app.engine.arbiter.pending_motions) == 1


def test_parallel_moves_for_both_colors():
    app = GuiApp(create_standard_board())

    app.controller.handle_click(*_cell_center(6, 4), 1000)
    app.controller.handle_click(*_cell_center(4, 4), 2000)
    assert len(app.engine.arbiter.pending_motions) == 1

    app.controller.handle_click(*_cell_center(1, 4), 3000)
    app.controller.handle_click(*_cell_center(3, 4), 4000)
    assert len(app.engine.arbiter.pending_motions) == 2


def test_captured_piece_not_displayed_after_capture():
    board = Board(8, 8)
    board.set_piece(6, 3, Piece("w", "P"))
    board.set_piece(5, 4, Piece("b", "P"))
    app = GuiApp(board)

    app.controller.handle_click(*_cell_center(6, 3), 1000)
    app.controller.handle_click(*_cell_center(5, 4), 2000)

    app.engine.advance_time(1000)
    app.piece_states.update(1000)

    black_pawns = [
        piece
        for piece in app.piece_states.pieces
        if piece.piece.color == "b" and piece.piece.kind == "P"
    ]
    assert black_pawns == []


def test_rest_timer_blocks_reselection_until_cooldown():
    board = Board(8, 8)
    board.set_piece(6, 4, Piece("w", "P"))
    app = GuiApp(board)

    app.controller.handle_click(*_cell_center(6, 4), 1000)
    app.controller.handle_click(*_cell_center(5, 4), 2000)
    app.engine.advance_time(1000)
    app.piece_states.update(1000)

    app.controller.handle_click(*_cell_center(5, 4), 3000)
    assert app.controller.selected_pos is None
    assert "resting" in app.controller.status_message.lower()


def test_friendly_rook_stops_one_square_before_shared_target():
    board = Board(8, 8)
    board.set_piece(7, 0, Piece("w", "R"))
    board.set_piece(7, 7, Piece("w", "R"))
    engine = GameEngine(board)

    first = engine.request_move(7, 0, 7, 4)
    second = engine.request_move(7, 7, 7, 4)

    assert first.allowed is True
    assert second.allowed is True
    assert engine.arbiter.pending_motions[1].to_row == 7
    assert engine.arbiter.pending_motions[1].to_col == 5


def test_friendly_knight_rejected_when_target_already_claimed():
    board = Board(8, 8)
    board.set_piece(7, 0, Piece("w", "R"))
    board.set_piece(6, 1, Piece("w", "N"))
    engine = GameEngine(board)

    engine.request_move(7, 0, 7, 3)
    result = engine.request_move(6, 1, 7, 3)

    assert result.allowed is False
    assert result.reason == "friendly_destination_conflict"
