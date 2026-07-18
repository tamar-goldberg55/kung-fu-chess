"""Per-piece visual state machine with logical rest blocking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from board import Board, GameEngine, Motion, move_duration_ms
from Grafic.grafic_config import LONG_REST_MS, SHORT_REST_MS
from piece import Piece


@dataclass
class TrackedPiece:
    piece_id: int
    piece: Piece
    row: int
    col: int
    visual_row: float
    visual_col: float
    state: str = "idle"
    state_start_ms: int = 0
    rest_until_ms: int = 0


class PieceStateManager:
    """Tracks animation states and enforces rest cooldowns for each piece."""

    def __init__(self, engine: GameEngine):
        self._engine = engine
        self._pieces: Dict[int, TrackedPiece] = {}
        self._cell_to_id: Dict[Tuple[int, int], int] = {}
        self._hidden_cells: Set[Tuple[int, int]] = set()
        self._next_id = 1
        self.sync_with_board()

    @property
    def pieces(self) -> List[TrackedPiece]:
        return list(self._pieces.values())

    def get_id_at(self, row: int, col: int) -> Optional[int]:
        return self._cell_to_id.get((row, col))

    def rest_remaining_ms(self, piece_id: int) -> int:
        tracked = self._pieces.get(piece_id)
        if tracked is None:
            return 0
        if tracked.state not in {"long_rest", "short_rest"}:
            return 0
        return max(0, tracked.rest_until_ms - self._engine.current_time)

    def is_resting(self, piece_id: int) -> bool:
        tracked = self._pieces.get(piece_id)
        if tracked is None:
            return False
        return tracked.state in {"long_rest", "short_rest"}

    def is_resting_at(self, row: int, col: int) -> bool:
        piece_id = self._cell_to_id.get((row, col))
        if piece_id is None:
            return False
        return self.is_resting(piece_id)

    def is_selectable(self, row: int, col: int) -> bool:
        if self._engine.board.get_piece(row, col) is None:
            return False
        if self.is_resting_at(row, col):
            return False
        if self._engine.arbiter.is_piece_moving(row, col):
            return False
        if self._engine.arbiter.is_piece_airborne(row, col):
            return False
        return True

    def on_move_scheduled(self, motion: Motion) -> None:
        """Remove captured pieces from the display as soon as capture is ordered."""
        target = self._engine.board.get_piece(motion.to_row, motion.to_col)
        if target is None or target.color == motion.piece.color:
            return
        victim_id = self._cell_to_id.get((motion.to_row, motion.to_col))
        if victim_id is None:
            return
        del self._cell_to_id[(motion.to_row, motion.to_col)]
        del self._pieces[victim_id]
        self._hidden_cells.add((motion.to_row, motion.to_col))

    def on_move_requested(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        piece_id = self._cell_to_id.get((from_row, from_col))
        if piece_id is None:
            return
        tracked = self._pieces[piece_id]
        self._set_state(tracked, "move", self._engine.current_time)

    def on_jump_requested(self, row: int, col: int) -> None:
        piece_id = self._cell_to_id.get((row, col))
        if piece_id is None:
            return
        tracked = self._pieces[piece_id]
        self._set_state(tracked, "jump", self._engine.current_time)

    def on_motion_completed(self, motion, time_ms: int) -> None:
        self._hidden_cells.discard((motion.to_row, motion.to_col))
        victim_id = self._cell_to_id.get((motion.to_row, motion.to_col))
        piece_id = self._find_id_for_motion(motion)
        if victim_id is not None and victim_id != piece_id:
            del self._cell_to_id[(motion.to_row, motion.to_col)]
            del self._pieces[victim_id]
        if piece_id is None:
            piece_id = self._cell_to_id.get((motion.to_row, motion.to_col))
        if piece_id is None:
            return
        tracked = self._pieces[piece_id]
        if (motion.from_row, motion.from_col) in self._cell_to_id:
            del self._cell_to_id[(motion.from_row, motion.from_col)]
        tracked.row = motion.to_row
        tracked.col = motion.to_col
        tracked.visual_row = float(motion.to_row)
        tracked.visual_col = float(motion.to_col)
        self._cell_to_id[(motion.to_row, motion.to_col)] = piece_id
        self._set_state(tracked, "long_rest", time_ms)
        tracked.rest_until_ms = time_ms + LONG_REST_MS

    def update(self, delta_ms: int) -> None:
        self._update_visual_positions()
        self._sync_board_positions()
        self._recover_stuck_states()
        current_time = self._engine.current_time
        for tracked in self._pieces.values():
            if tracked.state == "long_rest" and current_time >= tracked.rest_until_ms:
                self._set_state(tracked, "idle", current_time)
            elif tracked.state == "short_rest" and current_time >= tracked.rest_until_ms:
                self._set_state(tracked, "idle", current_time)
            elif tracked.state == "jump":
                if not self._engine.arbiter.is_piece_airborne(tracked.row, tracked.col):
                    self._set_state(tracked, "short_rest", current_time)
                    tracked.rest_until_ms = current_time + SHORT_REST_MS

    def sync_with_board(self) -> None:
        board = self._engine.board
        seen_cells = set()
        for row in range(board.height):
            for col in range(board.width):
                if (row, col) in self._hidden_cells:
                    continue
                piece = board.get_piece(row, col)
                if piece is None:
                    continue
                seen_cells.add((row, col))
                piece_id = self._cell_to_id.get((row, col))
                if piece_id is None:
                    piece_id = self._register_piece(piece, row, col)
                else:
                    tracked = self._pieces[piece_id]
                    tracked.piece = piece
                    tracked.row = row
                    tracked.col = col
        for cell, piece_id in list(self._cell_to_id.items()):
            if cell not in seen_cells:
                del self._cell_to_id[cell]
                del self._pieces[piece_id]

    def _register_piece(self, piece: Piece, row: int, col: int) -> int:
        piece_id = self._next_id
        self._next_id += 1
        tracked = TrackedPiece(
            piece_id=piece_id,
            piece=piece,
            row=row,
            col=col,
            visual_row=float(row),
            visual_col=float(col),
        )
        self._pieces[piece_id] = tracked
        self._cell_to_id[(row, col)] = piece_id
        return piece_id

    def _set_state(self, tracked: TrackedPiece, new_state: str, time_ms: int) -> None:
        tracked.state = new_state
        tracked.state_start_ms = time_ms

    def _find_id_for_motion(self, motion: Motion) -> Optional[int]:
        return self._cell_to_id.get((motion.from_row, motion.from_col))

    def _recover_stuck_states(self) -> None:
        moving_ids = set()
        for motion in self._engine.arbiter.pending_motions:
            piece_id = self._cell_to_id.get((motion.from_row, motion.from_col))
            if piece_id is not None:
                moving_ids.add(piece_id)

        for tracked in self._pieces.values():
            if tracked.state == "move" and tracked.piece_id not in moving_ids:
                tracked.state = "idle"
            if tracked.state == "jump" and not self._engine.arbiter.is_piece_airborne(
                tracked.row, tracked.col
            ):
                tracked.state = "idle"

    def _sync_board_positions(self) -> None:
        self.sync_with_board()

    def _update_visual_positions(self) -> None:
        current_time = self._engine.current_time
        for motion in self._engine.arbiter.pending_motions:
            piece_id = self._cell_to_id.get((motion.from_row, motion.from_col))
            if piece_id is None:
                continue
            tracked = self._pieces[piece_id]
            travel_ms = move_duration_ms(
                motion.piece.kind,
                motion.from_row,
                motion.from_col,
                motion.to_row,
                motion.to_col,
            )
            start_time = motion.arrival_time - travel_ms
            if travel_ms <= 0:
                progress = 1.0
            else:
                progress = max(0.0, min(1.0, (current_time - start_time) / travel_ms))
            tracked.visual_row = motion.from_row + (motion.to_row - motion.from_row) * progress
            tracked.visual_col = motion.from_col + (motion.to_col - motion.from_col) * progress
            tracked.state = "move"

            if progress >= 1.0:
                target = self._engine.board.get_piece(motion.to_row, motion.to_col)
                if target is not None and target.color != motion.piece.color:
                    self._hidden_cells.add((motion.to_row, motion.to_col))

        for airborne in self._engine.arbiter.airborne_pieces:
            piece_id = self._cell_to_id.get((airborne["row"], airborne["col"]))
            if piece_id is None:
                continue
            tracked = self._pieces[piece_id]
            tracked.state = "jump"
            tracked.visual_row = float(airborne["row"])
            tracked.visual_col = float(airborne["col"])

        moving_ids = set()
        for motion in self._engine.arbiter.pending_motions:
            piece_id = self._cell_to_id.get((motion.from_row, motion.from_col))
            if piece_id is not None:
                moving_ids.add(piece_id)

        for tracked in self._pieces.values():
            if tracked.piece_id in moving_ids or tracked.state in {"jump", "move"}:
                continue
            tracked.visual_row = float(tracked.row)
            tracked.visual_col = float(tracked.col)
