"""Observer that tracks captured-piece score per color."""

from __future__ import annotations

from dataclasses import dataclass

from board import MotionCompletedEvent
from Grafic.grafic_config import PIECE_SCORES


@dataclass
class ScoreState:
    white: int = 0
    black: int = 0


class ScoreObserver:
    """Updates score asynchronously from completed motions."""

    def __init__(self):
        self.state = ScoreState()

    def on_motion_completed(self, event: MotionCompletedEvent) -> None:
        captured = event.captured
        if captured is None:
            return
        points = PIECE_SCORES.get(captured.kind, 0)
        mover_color = event.motion.piece.color
        if mover_color == "w":
            self.state.white += points
        else:
            self.state.black += points
