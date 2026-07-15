"""Board model, motion engine, and game orchestration."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from config import JUMP_DURATION, MOVE_DURATION
from piece import Piece


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cells: List[List[Optional[Piece]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        self._cells[row][col] = piece

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self._cells[row][col]


class RuleContext:
    """Read-only context for move validation against board state."""

    def __init__(self, board: Board, pending_targets: Optional[Set[Tuple[int, int]]] = None):
        self.board = board
        self._pending_targets = pending_targets or set()

    @property
    def width(self) -> int:
        return self.board.width

    @property
    def height(self) -> int:
        return self.board.height

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self.board.get_piece(row, col)

    def is_target_occupied_by_pending(self, row: int, col: int) -> bool:
        return (row, col) in self._pending_targets

    def is_destination_allowed(self, to_row: int, to_col: int, piece_color: str) -> bool:
        target = self.get_piece(to_row, to_col)
        if target is None:
            return True
        return target.color != piece_color


@dataclass
class Motion:
    piece: Piece
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    arrival_time: int
    scheduled_order: int = 0


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    reason: Optional[str] = None


def move_duration_ms(piece_kind: str, from_row: int, from_col: int, to_row: int, to_col: int) -> int:
    """Travel time scales with distance; knights take longer per hop."""
    distance = max(abs(to_row - from_row), abs(to_col - from_col))
    if piece_kind == "N":
        return MOVE_DURATION * 3
    return MOVE_DURATION * max(distance, 1)


def one_square_before(
    from_row: int,
    from_col: int,
    to_row: int,
    to_col: int,
) -> Tuple[int, int]:
    """Return the cell one step before the destination along a straight line."""
    row_step = 0 if to_row == from_row else (1 if to_row > from_row else -1)
    col_step = 0 if to_col == from_col else (1 if to_col > from_col else -1)
    prev_row, prev_col = from_row, from_col
    curr_row, curr_col = from_row + row_step, from_col + col_step
    while (curr_row, curr_col) != (to_row, to_col):
        prev_row, prev_col = curr_row, curr_col
        curr_row += row_step
        curr_col += col_step
    return prev_row, prev_col


class RealTimeArbiter:
    """Schedules motions and resolves arrivals in deterministic order."""

    def __init__(self):
        self.pending_motions: List[Motion] = []
        self.airborne_pieces: List[Dict[str, Any]] = []
        self._next_order = 0

    def get_pending_targets(self) -> Set[Tuple[int, int]]:
        return {(motion.to_row, motion.to_col) for motion in self.pending_motions}

    def has_active_motion_for(
        self, from_row: int, from_col: int, to_row: int, to_col: int
    ) -> bool:
        if self.is_piece_moving(from_row, from_col):
            return True
        for motion in self.pending_motions:
            if motion.to_row == to_row and motion.to_col == to_col:
                if motion.from_row != from_row or motion.from_col != from_col:
                    return True
        return False

    def is_piece_moving(self, row: int, col: int) -> bool:
        return any(m.from_row == row and m.from_col == col for m in self.pending_motions)

    def is_piece_airborne(self, row: int, col: int) -> bool:
        return any(a["row"] == row and a["col"] == col for a in self.airborne_pieces)

    def schedule_motion(self, motion: Motion) -> None:
        motion.scheduled_order = self._next_order
        self._next_order += 1
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
        on_motion_completed: Optional[Callable[[Motion, Optional[Piece]], None]] = None,
    ) -> None:
        self.pending_motions.sort(
            key=lambda motion: (motion.arrival_time, motion.scheduled_order)
        )
        completed: List[Motion] = []
        for motion in self.pending_motions:
            if current_time >= motion.arrival_time:
                self._apply_motion(
                    board, motion, on_capture, on_promotion, on_motion_completed
                )
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
        on_motion_completed: Optional[Callable[[Motion, Optional[Piece]], None]] = None,
    ) -> None:
        if self._resolve_airborne_interception(motion):
            board.set_piece(motion.from_row, motion.from_col, None)
            if on_motion_completed is not None:
                on_motion_completed(motion, None)
            return

        source_piece = board.get_piece(motion.from_row, motion.from_col)
        if source_piece is None or source_piece.color != motion.piece.color:
            return

        target = board.get_piece(motion.to_row, motion.to_col)
        if target is None or target.color != motion.piece.color:
            captured = target if target is not None and target.color != motion.piece.color else None
            on_capture(target)
            board.set_piece(motion.to_row, motion.to_col, motion.piece)
            board.set_piece(motion.from_row, motion.from_col, None)
            on_promotion(motion.to_row, motion.to_col)
            if on_motion_completed is not None:
                on_motion_completed(motion, captured)


@dataclass(frozen=True)
class MotionCompletedEvent:
    motion: Motion
    captured: Optional[Piece]
    time_ms: int


class GameEngine:
    """Gateway for move requests, time advancement, and game-over state."""

    def __init__(self, board: Board):
        from rules import RuleEngine

        self.board = board
        self.rule_engine = RuleEngine()
        self.arbiter = RealTimeArbiter()
        self._current_time = 0
        self._game_over = False
        self._listeners: List[Any] = []

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

        if self.arbiter.is_piece_moving(from_row, from_col):
            return ValidationResult(False, "piece_already_moving")

        adjusted = self._adjust_friendly_destination(piece, from_row, from_col, to_row, to_col)
        if adjusted is None:
            return ValidationResult(False, "friendly_destination_conflict")
        to_row, to_col = adjusted

        if self.arbiter.has_active_motion_for(from_row, from_col, to_row, to_col):
            return ValidationResult(False, "active_motion_conflict")

        context = RuleContext(self.board, self.arbiter.get_pending_targets())
        result = self.rule_engine.validate(context, from_row, from_col, to_row, to_col, piece)
        if not result.allowed:
            return result

        travel_ms = move_duration_ms(piece.kind, from_row, from_col, to_row, to_col)
        motion = Motion(
            piece=piece,
            from_row=from_row,
            from_col=from_col,
            to_row=to_row,
            to_col=to_col,
            arrival_time=self._current_time + travel_ms,
        )
        self.arbiter.schedule_motion(motion)
        self._notify_move_scheduled(motion)
        return ValidationResult(True)

    def _adjust_friendly_destination(
        self,
        piece: Piece,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
    ) -> Optional[Tuple[int, int]]:
        """Resolve two friendly pieces targeting the same square."""
        for motion in self.arbiter.pending_motions:
            if motion.to_row != to_row or motion.to_col != to_col:
                continue
            if motion.piece.color != piece.color:
                continue
            if motion.from_row == from_row and motion.from_col == from_col:
                continue
            if piece.kind in ("R", "B", "Q"):
                stop_row, stop_col = one_square_before(from_row, from_col, to_row, to_col)
                if (stop_row, stop_col) == (from_row, from_col):
                    return None
                return stop_row, stop_col
            return None
        return to_row, to_col

    def _notify_move_scheduled(self, motion: Motion) -> None:
        for listener in self._listeners:
            if hasattr(listener, "on_move_scheduled"):
                listener.on_move_scheduled(motion, self._current_time)

    def request_jump(self, row: int, col: int) -> bool:
        if self._game_over:
            return False
        return self.arbiter.start_jump(self.board, row, col, self._current_time)

    def add_listener(self, listener: Any) -> None:
        self._listeners.append(listener)

    def advance_time(self, time_delta: int) -> None:
        self._current_time += time_delta

        def _on_motion_completed(motion: Motion, captured: Optional[Piece]) -> None:
            event = MotionCompletedEvent(motion=motion, captured=captured, time_ms=self._current_time)
            for listener in self._listeners:
                if hasattr(listener, "on_motion_completed"):
                    listener.on_motion_completed(event)

        self.arbiter.process_arrivals(
            self._current_time,
            self.board,
            self._on_capture,
            self._on_promotion,
            on_motion_completed=_on_motion_completed,
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
