"""Central application service for all game actions."""

from typing import Optional

from board import Board
from config import MOVE_DURATION
from motion import Motion
from piece import Piece
from real_time_arbiter import RealTimeArbiter
from rule_context import RuleContext
from rule_engine import RuleEngine, ValidationResult


class GameEngine:
    """Gateway for move requests, time advancement, and game-over state."""

    def __init__(self, board: Board):
        self.board = board
        self.rule_engine = RuleEngine()
        self.arbiter = RealTimeArbiter()
        self._current_time = 0
        self._game_over = False

    @property
    def current_time(self) -> int:
        return self._current_time

    @property
    def game_over(self) -> bool:
        return self._game_over

    def request_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> ValidationResult:
        if self._game_over:
            return ValidationResult(False, "game_over")

        piece = self.board.get_piece(from_row, from_col)
        if piece is None:
            return ValidationResult(False, "no_piece_at_source")

        if self.arbiter.has_active_motion_for(from_row, from_col, to_row, to_col):
            return ValidationResult(False, "active_motion_conflict")

        if self.arbiter.is_piece_moving(from_row, from_col):
            return ValidationResult(False, "piece_already_moving")

        context = RuleContext(self.board, self.arbiter.get_pending_targets())
        result = self.rule_engine.validate(context, from_row, from_col, to_row, to_col, piece)
        if not result.allowed:
            return result

        motion = Motion(
            piece=piece,
            from_row=from_row,
            from_col=from_col,
            to_row=to_row,
            to_col=to_col,
            arrival_time=self._current_time + MOVE_DURATION,
        )
        self.arbiter.schedule_motion(motion)
        return ValidationResult(True)

    def request_jump(self, row: int, col: int) -> bool:
        if self._game_over:
            return False
        return self.arbiter.start_jump(self.board, row, col, self._current_time)

    def advance_time(self, time_delta: int) -> None:
        self._current_time += time_delta
        self.arbiter.process_arrivals(
            self._current_time,
            self.board,
            self._on_capture,
            self._on_promotion,
        )

    def force_all_moves(self) -> None:
        self.arbiter.force_all(self.board, self._on_capture, self._on_promotion)

    def _on_capture(self, captured: Optional[Piece]) -> None:
        if captured is not None and captured.kind == "K":
            self._game_over = True

    def _on_promotion(self, row: int, col: int) -> None:
        piece = self.board.get_piece(row, col)
        if piece is None or piece.kind != "P":
            return
        last_row = 0 if piece.color == "w" else self.board.height - 1
        if row == last_row:
            self.board.set_piece(row, col, Piece(piece.color, "Q"))
