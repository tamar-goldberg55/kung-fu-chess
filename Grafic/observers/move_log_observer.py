"""Observer that records move history per player color."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from board import Motion, MotionCompletedEvent
from Grafic.algebraic import format_move, format_time_ms


@dataclass
class MoveLogState:
    white_moves: List[Tuple[str, str]] = field(default_factory=list)
    black_moves: List[Tuple[str, str]] = field(default_factory=list)


class MoveLogObserver:
    """Stores move text and game-time for each color."""

    def __init__(self, board_height: int):
        self._board_height = board_height
        self.state = MoveLogState()

    def on_move_scheduled(self, motion: Motion, time_ms: int) -> None:
        """Log immediately when the player orders a move."""
        self._append_move(motion, time_ms)

    def on_motion_completed(self, event: MotionCompletedEvent) -> None:
        """Keep completion events for tests; avoid duplicate log lines."""
        return

    def _append_move(self, motion: Motion, time_ms: int) -> None:
        move_text = format_move(
            motion.piece,
            motion.from_row,
            motion.from_col,
            motion.to_row,
            motion.to_col,
            self._board_height,
        )
        time_text = format_time_ms(time_ms)
        entry = (time_text, move_text)
        if motion.piece.color == "w":
            self.state.white_moves.append(entry)
        else:
            self.state.black_moves.append(entry)
