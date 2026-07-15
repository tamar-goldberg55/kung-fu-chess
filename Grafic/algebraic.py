"""Convert board coordinates to human-readable chess notation."""

from Grafic.grafic_config import PIECE_NAMES
from piece import Piece


def cell_to_square(row: int, col: int, board_height: int) -> str:
    file_letter = chr(ord("a") + col)
    rank_number = board_height - row
    return f"{file_letter}{rank_number}"


def format_move(piece: Piece, from_row: int, from_col: int, to_row: int, to_col: int, board_height: int) -> str:
    piece_name = PIECE_NAMES.get(piece.kind, piece.kind)
    start = cell_to_square(from_row, from_col, board_height)
    end = cell_to_square(to_row, to_col, board_height)
    return f"{piece_name}: {start}->{end}"


def format_time_ms(time_ms: int) -> str:
    return f"{time_ms / 1000:.1f}s"


def format_cell(row: int, col: int, board_height: int) -> str:
    return cell_to_square(row, col, board_height)


def format_legal_hint(cells: list[tuple[int, int]], board_height: int) -> str:
    if not cells:
        return "no legal moves"
    squares = [format_cell(row, col, board_height) for row, col in cells[:4]]
    return ", ".join(squares)
