"""Read-only snapshot DTO for rendering one game frame."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from Grafic.observers.move_log_observer import MoveLogState
from Grafic.observers.score_observer import ScoreState
from Grafic.piece_state_manager import PieceStateManager, TrackedPiece
from Grafic.sprite_manager import SpriteManager
from board import GameEngine
from Grafic.gfx_controller import GfxController


@dataclass(frozen=True)
class PieceView:
    piece_id: int
    token: str
    visual_row: float
    visual_col: float
    state: str
    is_selected: bool
    elapsed_state_ms: int
    rest_remaining_ms: int


@dataclass(frozen=True)
class GameSnapshot:
    board_width: int
    board_height: int
    current_time_ms: int
    pieces: Tuple[PieceView, ...]
    score: ScoreState
    move_log: MoveLogState
    game_over: bool
    selected_pos: Optional[Tuple[int, int]]
    last_click_pos: Optional[Tuple[int, int]]
    active_moves: int
    status_message: str
    legal_moves: Tuple[Tuple[int, int], ...]
    threatened_squares: Tuple[Tuple[int, int], ...]


class GameSnapshotBuilder:
    """Builds a render snapshot from engine, sprites, and observers."""

    def __init__(
        self,
        engine: GameEngine,
        controller: GfxController,
        piece_states: PieceStateManager,
        sprite_manager: SpriteManager,
        score_state: ScoreState,
        move_log_state: MoveLogState,
    ):
        self._engine = engine
        self._controller = controller
        self._piece_states = piece_states
        self._sprite_manager = sprite_manager
        self._score_state = score_state
        self._move_log_state = move_log_state

    def build(self) -> GameSnapshot:
        current_time = self._engine.current_time
        selected_pos = self._controller.selected_pos
        piece_views: List[PieceView] = []

        for tracked in self._piece_states.pieces:
            elapsed = max(0, current_time - tracked.state_start_ms)
            piece_views.append(
                PieceView(
                    piece_id=tracked.piece_id,
                    token=tracked.piece.to_token(),
                    visual_row=tracked.visual_row,
                    visual_col=tracked.visual_col,
                    state=tracked.state,
                    is_selected=selected_pos == (tracked.row, tracked.col),
                    elapsed_state_ms=elapsed,
                    rest_remaining_ms=self._piece_states.rest_remaining_ms(tracked.piece_id),
                )
            )

        return GameSnapshot(
            board_width=self._engine.board.width,
            board_height=self._engine.board.height,
            current_time_ms=current_time,
            pieces=tuple(piece_views),
            score=self._score_state,
            move_log=self._move_log_state,
            game_over=self._engine.game_over,
            selected_pos=selected_pos,
            last_click_pos=self._controller.last_click_pos,
            active_moves=len(self._engine.arbiter.pending_motions),
            status_message=self._controller.status_message,
            legal_moves=tuple(self._controller.legal_moves),
            threatened_squares=tuple(self._controller.threatened_squares()),
        )

    def get_sprite_for_piece_view(self, tracked: TrackedPiece, elapsed_ms: int):
        return self._sprite_manager.get_frame(tracked.piece, tracked.state, elapsed_ms)
