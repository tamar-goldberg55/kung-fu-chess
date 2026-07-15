"""Integration test for GUI click-to-move flow."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Grafic.default_board import create_standard_board
from Grafic.grafic_config import CELL_SIZE, HEADER_HEIGHT, SIDE_PANEL_WIDTH
from Grafic.gui_main import GuiApp


def _cell_center(row: int, col: int) -> tuple[int, int]:
    x = SIDE_PANEL_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
    y = HEADER_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def test_click_select_and_move_advances_piece():
    app = GuiApp(create_standard_board())

    pawn_row, pawn_col = 6, 4
    dest_row, dest_col = 4, 4
    app.controller.handle_click(*_cell_center(pawn_row, pawn_col), 1000)
    assert app.controller.selected_pos == (pawn_row, pawn_col)

    app.controller.handle_click(*_cell_center(dest_row, dest_col), 2000)
    assert len(app.engine.arbiter.pending_motions) == 1

    app.engine.advance_time(2500)
    app.piece_states.update(2500)

    assert app.engine.board.get_piece(dest_row, dest_col) is not None
    assert app.engine.board.get_piece(pawn_row, pawn_col) is None
    assert app.move_log_observer.state.white_moves
