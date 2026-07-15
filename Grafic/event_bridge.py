"""Forwards engine motion events to observers and piece state manager."""

from __future__ import annotations

from board import MotionCompletedEvent
from Grafic.observers.move_log_observer import MoveLogObserver
from Grafic.observers.score_observer import ScoreObserver
from Grafic.piece_state_manager import PieceStateManager


class GfxEventBridge:
    """Single listener that fans out motion-completed events."""

    def __init__(
        self,
        piece_states: PieceStateManager,
        score_observer: ScoreObserver,
        move_log_observer: MoveLogObserver,
    ):
        self._piece_states = piece_states
        self._score_observer = score_observer
        self._move_log_observer = move_log_observer

    def on_motion_completed(self, event: MotionCompletedEvent) -> None:
        self._piece_states.on_motion_completed(event.motion, event.time_ms)
        self._score_observer.on_motion_completed(event)

    def on_move_scheduled(self, motion, time_ms: int) -> None:
        self._piece_states.on_move_scheduled(motion)
        self._move_log_observer.on_move_scheduled(motion, time_ms)
