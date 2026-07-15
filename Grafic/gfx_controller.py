"""Graphical game controller with double-click jump and rest blocking."""

from __future__ import annotations

from typing import List, Optional, Tuple

from board import GameEngine
from board_mapper import InvalidCoordinatesError
from Grafic.algebraic import format_cell, format_legal_hint
from Grafic.grafic_config import DOUBLE_CLICK_MS
from Grafic.legal_moves import legal_destinations
from Grafic.piece_state_manager import PieceStateManager
from Grafic.window_mapper import WindowMapper
from piece import Piece


class GfxController:
    """Handles clicks for the GUI while respecting visual rest states."""

    def __init__(self, engine: GameEngine, mapper: WindowMapper, piece_states: PieceStateManager):
        self.engine = engine
        self.mapper = mapper
        self.piece_states = piece_states
        self._selected_piece: Optional[Piece] = None
        self._selected_pos: Optional[Tuple[int, int]] = None
        self._last_click_cell: Optional[Tuple[int, int]] = None
        self._last_click_time_ms: int = -1
        self.last_click_pos: Optional[Tuple[int, int]] = None
        self.legal_moves: List[Tuple[int, int]] = []
        self.status_message: str = "Click your piece, then click a green square"

    @property
    def selected_pos(self) -> Optional[Tuple[int, int]]:
        return self._selected_pos

    def handle_click(self, image_x: int, image_y: int, click_time_ms: int) -> None:
        if self.engine.game_over:
            self.status_message = "Game over"
            return
        try:
            row, col = self.mapper.to_cell(image_x, image_y)
        except InvalidCoordinatesError:
            self.last_click_pos = None
            self.status_message = "Click on the board squares only"
            return

        self.last_click_pos = (row, col)

        if self._is_double_click(row, col, click_time_ms):
            if self._selected_pos == (row, col):
                self._try_jump(row, col)
            self._last_click_cell = None
            self._last_click_time_ms = -1
            return

        self._last_click_cell = (row, col)
        self._last_click_time_ms = click_time_ms

        piece = self.engine.board.get_piece(row, col)
        is_unselectable = self._is_unselectable(row, col)

        if self._selected_piece and self._selected_pos:
            from_row, from_col = self._selected_pos
            if (row, col) == (from_row, from_col):
                self.status_message = self._destination_hint(from_row, from_col)
                return
            if self._is_unselectable(from_row, from_col):
                self.status_message = "Piece is resting - wait for timer"
                self._clear_selection()
                return
            result = self.engine.request_move(from_row, from_col, row, col)
            if result.allowed:
                self.piece_states.on_move_requested(from_row, from_col, row, col)
                self.status_message = f"Moving {format_cell(from_row, from_col, self.engine.board.height)} -> {format_cell(row, col, self.engine.board.height)}"
                self._clear_selection()
            elif piece and not is_unselectable and piece.color == self._selected_piece.color:
                self._select_piece(piece, row, col)
            else:
                clicked = format_cell(row, col, self.engine.board.height)
                hints = format_legal_hint(self.legal_moves, self.engine.board.height)
                if piece and piece.color != self._selected_piece.color:
                    self.status_message = f"Capture {clicked} via green square ({hints})"
                else:
                    self.status_message = f"Illegal click {clicked} - choose green square: {hints}"
        elif piece and not is_unselectable:
            self._select_piece(piece, row, col)
        else:
            if piece and is_unselectable:
                self.status_message = "Piece is resting - wait for timer"
            else:
                self.status_message = "No piece here - click a piece on the board"

    def _select_piece(self, piece: Piece, row: int, col: int) -> None:
        self._selected_piece = piece
        self._selected_pos = (row, col)
        self.legal_moves = legal_destinations(self.engine, row, col)
        self.status_message = self._selection_message(row, col)

    def _selection_message(self, row: int, col: int) -> str:
        square = format_cell(row, col, self.engine.board.height)
        hints = format_legal_hint(self.legal_moves, self.engine.board.height)
        return f"Selected {square} - click a green square ({hints})"

    def _destination_hint(self, row: int, col: int) -> str:
        square = format_cell(row, col, self.engine.board.height)
        hints = format_legal_hint(self.legal_moves, self.engine.board.height)
        return f"Piece selected at {square} - now click GREEN destination: {hints}"

    def _is_unselectable(self, row: int, col: int) -> bool:
        if self.piece_states.is_resting_at(row, col):
            return True
        if self.engine.arbiter.is_piece_moving(row, col):
            return True
        if self.engine.arbiter.is_piece_airborne(row, col):
            return True
        return False

    def _is_double_click(self, row: int, col: int, click_time_ms: int) -> bool:
        if self._last_click_cell != (row, col):
            return False
        if self._last_click_time_ms < 0:
            return False
        return click_time_ms - self._last_click_time_ms <= DOUBLE_CLICK_MS

    def _try_jump(self, row: int, col: int) -> None:
        if self._is_unselectable(row, col):
            return
        if self.engine.request_jump(row, col):
            self.piece_states.on_jump_requested(row, col)
            self.status_message = f"Jump at {format_cell(row, col, self.engine.board.height)}"
            self._clear_selection()

    def _clear_selection(self) -> None:
        self._selected_piece = None
        self._selected_pos = None
        self.legal_moves = []
