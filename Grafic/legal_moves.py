"""Compute legal destination cells for the selected piece."""

from __future__ import annotations

from typing import List, Tuple

from board import Board, GameEngine, RuleContext
from piece import Piece


def legal_destinations(engine: GameEngine, from_row: int, from_col: int) -> List[Tuple[int, int]]:
    board = engine.board
    piece = board.get_piece(from_row, from_col)
    if piece is None:
        return []

    context = RuleContext(board, engine.arbiter.get_pending_targets())
    destinations: List[Tuple[int, int]] = []

    for row in range(board.height):
        for col in range(board.width):
            if (row, col) == (from_row, from_col):
                continue
            result = engine.rule_engine.validate(context, from_row, from_col, row, col, piece)
            if result.allowed:
                destinations.append((row, col))

    return destinations
