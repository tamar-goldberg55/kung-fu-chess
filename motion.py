"""In-flight motion representation."""

from dataclasses import dataclass

from piece import Piece


@dataclass
class Motion:
    piece: Piece
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    arrival_time: int
