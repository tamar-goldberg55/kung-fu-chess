"""Detect pieces threatened by an incoming enemy capture."""

from __future__ import annotations

from board import GameEngine


def is_threatened_by_capture(engine: GameEngine, row: int, col: int) -> bool:
    """Return True when an enemy motion is heading to this square to capture."""
    piece = engine.board.get_piece(row, col)
    if piece is None:
        return False

    for motion in engine.arbiter.pending_motions:
        if motion.to_row != row or motion.to_col != col:
            continue
        if motion.piece.color == piece.color:
            continue
        target = engine.board.get_piece(motion.to_row, motion.to_col)
        if target is not None and target.color != motion.piece.color:
            return True
    return False
