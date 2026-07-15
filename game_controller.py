"""Handles click selection and delegates moves to the GameEngine."""

from typing import Optional, Tuple

from board_mapper import BoardMapper, InvalidCoordinatesError
from game_engine import GameEngine
from piece import Piece


class GameController:
    """Translates user clicks into GameEngine request_move calls."""

    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.mapper = BoardMapper(engine.board)
        self._selected_piece: Optional[Piece] = None
        self._selected_pos: Optional[Tuple[int, int]] = None

    def handle_click(self, x: int, y: int) -> None:
        if self.engine.game_over:
            return
        try:
            row, col = self.mapper.to_cell(x, y)
        except InvalidCoordinatesError:
            return

        piece = self.engine.board.get_piece(row, col)
        is_unselectable = (
            self.engine.arbiter.is_piece_moving(row, col)
            or self.engine.arbiter.is_piece_airborne(row, col)
        )

        if self._selected_piece and self._selected_pos:
            result = self.engine.request_move(
                self._selected_pos[0], self._selected_pos[1], row, col
            )
            if result.allowed:
                self._selected_piece = None
                self._selected_pos = None
            elif piece and not is_unselectable:
                self._selected_piece = piece
                self._selected_pos = (row, col)
            else:
                self._selected_piece = None
                self._selected_pos = None
        elif piece and not is_unselectable:
            self._selected_piece = piece
            self._selected_pos = (row, col)

    def handle_jump(self, x: int, y: int) -> None:
        if self.engine.game_over:
            return
        try:
            row, col = self.mapper.to_cell(x, y)
        except InvalidCoordinatesError:
            return
        self.engine.request_jump(row, col)
