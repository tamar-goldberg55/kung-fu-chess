"""Deterministic virtual-time manager for parallel piece motions."""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from board import Board
from config import JUMP_DURATION, MOVE_DURATION
from motion import Motion
from piece import Piece


class RealTimeArbiter:
    """Schedules motions and resolves arrivals in deterministic order."""

    def __init__(self):
        self.pending_motions: List[Motion] = []
        self.airborne_pieces: List[Dict[str, Any]] = []

    def get_pending_targets(self) -> Set[Tuple[int, int]]:
        return {(motion.to_row, motion.to_col) for motion in self.pending_motions}

    def has_active_motion_for(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        for motion in self.pending_motions:
            if motion.from_row == from_row and motion.from_col == from_col:
                return True
            if motion.to_row == to_row and motion.to_col == to_col:
                return True
        return False

    def is_piece_moving(self, row: int, col: int) -> bool:
        return any(m.from_row == row and m.from_col == col for m in self.pending_motions)

    def is_piece_airborne(self, row: int, col: int) -> bool:
        return any(a["row"] == row and a["col"] == col for a in self.airborne_pieces)

    def schedule_motion(self, motion: Motion) -> None:
        self.pending_motions.append(motion)

    def start_jump(self, board: Board, row: int, col: int, current_time: int) -> bool:
        piece = board.get_piece(row, col)
        if piece is None:
            return False
        if self.is_piece_moving(row, col) or self.is_piece_airborne(row, col):
            return False
        self.airborne_pieces.append(
            {
                "piece": piece,
                "row": row,
                "col": col,
                "land_time": current_time + JUMP_DURATION,
            }
        )
        return True

    def process_arrivals(
        self,
        current_time: int,
        board: Board,
        on_capture: Callable[[Optional[Piece]], None],
        on_promotion: Callable[[int, int], None],
    ) -> None:
        self.pending_motions.sort(key=lambda motion: motion.arrival_time)
        completed: List[Motion] = []
        for motion in self.pending_motions:
            if current_time >= motion.arrival_time:
                self._apply_motion(board, motion, on_capture, on_promotion)
                completed.append(motion)
        for motion in completed:
            self.pending_motions.remove(motion)
        self._land_airborne(current_time)

    def force_all(
        self,
        board: Board,
        on_capture: Callable[[Optional[Piece]], None],
        on_promotion: Callable[[int, int], None],
    ) -> None:
        for motion in self.pending_motions[:]:
            self._apply_motion(board, motion, on_capture, on_promotion)
        self.pending_motions.clear()
        self.airborne_pieces.clear()

    def _land_airborne(self, current_time: int) -> None:
        self.airborne_pieces = [
            airborne for airborne in self.airborne_pieces if current_time < airborne["land_time"]
        ]

    def _resolve_airborne_interception(self, motion: Motion) -> bool:
        for airborne in self.airborne_pieces:
            if airborne["row"] == motion.to_row and airborne["col"] == motion.to_col:
                if airborne["piece"].color != motion.piece.color:
                    self.airborne_pieces.remove(airborne)
                    return True
        return False

    def _apply_motion(
        self,
        board: Board,
        motion: Motion,
        on_capture: Callable[[Optional[Piece]], None],
        on_promotion: Callable[[int, int], None],
    ) -> None:
        if self._resolve_airborne_interception(motion):
            board.set_piece(motion.from_row, motion.from_col, None)
            return

        target = board.get_piece(motion.to_row, motion.to_col)
        if target is None or target.color != motion.piece.color:
            on_capture(target)
            board.set_piece(motion.to_row, motion.to_col, motion.piece)
            board.set_piece(motion.from_row, motion.from_col, None)
            on_promotion(motion.to_row, motion.to_col)
