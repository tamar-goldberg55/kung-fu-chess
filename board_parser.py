"""Parses raw fixture text into a Board model."""

from typing import List

from board import Board
from board_format import BoardFormatError, validate_non_empty, validate_rectangular
from config import EMPTY_CELL
from piece import InvalidPieceTokenError, Piece


def _split_rows(text: str) -> List[List[str]]:
    raw_lines = text.splitlines()

    if "Board:" not in text:
        return [line.split() for line in raw_lines if line.strip() != ""]

    board_lines = []
    inside_board = False

    for line in raw_lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        if cleaned_line.startswith("Board:"):
            inside_board = True
            continue
        if cleaned_line.startswith("Commands:"):
            inside_board = False
            break
        if inside_board:
            board_lines.append(cleaned_line.split())

    return board_lines


def parse_board(text: str) -> Board:
    raw_rows = _split_rows(text)

    validate_non_empty(raw_rows)

    try:
        validate_rectangular(raw_rows)
    except BoardFormatError:
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")

    for row in raw_rows:
        for token in row:
            if token != EMPTY_CELL:
                try:
                    Piece.from_token(token)
                except Exception:
                    raise InvalidPieceTokenError("ERROR UNKNOWN_TOKEN")

    height = len(raw_rows)
    width = len(raw_rows[0])
    board = Board(width, height)

    for row_index, row_tokens in enumerate(raw_rows):
        for col_index, token in enumerate(row_tokens):
            if token == EMPTY_CELL:
                continue
            board.set_piece(row_index, col_index, Piece.from_token(token))

    return board
