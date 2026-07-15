"""Board parsing, rendering, game control, and text test runner."""

import sys
from dataclasses import dataclass
from typing import List, Optional, TextIO, Tuple

from board import Board, GameEngine
from board_mapper import BoardMapper, InvalidCoordinatesError
from config import CELL_SEPARATOR, EMPTY_CELL
from piece import InvalidPieceTokenError, Piece
from rules import BoardFormatError, validate_non_empty, validate_rectangular


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


@dataclass(frozen=True)
class BoardDTO:
    width: int
    height: int
    rows: Tuple[Tuple[str, ...], ...]


class BoardViewAdapter:
    def to_dto(self, board: Board) -> BoardDTO:
        rows: List[Tuple[str, ...]] = []
        for row_index in range(board.height):
            tokens = []
            for col_index in range(board.width):
                piece = board.get_piece(row_index, col_index)
                tokens.append(piece.to_token() if piece else EMPTY_CELL)
            rows.append(tuple(tokens))
        return BoardDTO(width=board.width, height=board.height, rows=tuple(rows))

    def render(self, board: Board) -> str:
        dto = self.to_dto(board)
        lines = [CELL_SEPARATOR.join(row) for row in dto.rows]
        return "\n".join(lines)


_adapter = BoardViewAdapter()


def render_board(board: Board) -> str:
    return _adapter.render(board)


class PrintBoard:
    def __init__(self, output_stream: TextIO = sys.stdout):
        self._output = output_stream
        self._adapter = BoardViewAdapter()

    def print(self, board: Board) -> None:
        print(self._adapter.render(board), file=self._output)


class GameController:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.mapper = BoardMapper(engine.board)
        self._selected_piece: Optional[Piece] = None
        self._selected_pos: Optional[Tuple[int, int]] = None

    def handle_click(self, x: int, y: int) -> None:
        if self.engine.game_over:
            return
        try:
            row, col = self.mapper.to_cell(x, y)
        except InvalidCoordinatesError:
            return

        piece = self.engine.board.get_piece(row, col)
        is_unselectable = (
            self.engine.arbiter.is_piece_moving(row, col)
            or self.engine.arbiter.is_piece_airborne(row, col)
        )

        if self._selected_piece and self._selected_pos:
            result = self.engine.request_move(
                self._selected_pos[0], self._selected_pos[1], row, col
            )
            if result.allowed:
                self._selected_piece = None
                self._selected_pos = None
            elif piece and not is_unselectable:
                self._selected_piece = piece
                self._selected_pos = (row, col)
            else:
                self._selected_piece = None
                self._selected_pos = None
        elif piece and not is_unselectable:
            self._selected_piece = piece
            self._selected_pos = (row, col)

    def handle_jump(self, x: int, y: int) -> None:
        if self.engine.game_over:
            return
        try:
            row, col = self.mapper.to_cell(x, y)
        except InvalidCoordinatesError:
            return
        self.engine.request_jump(row, col)


class TextTestRunner:
    def __init__(self, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
        self._input = input_stream
        self._output = output_stream

    def run(self) -> None:
        text = self._input.read()
        board = parse_board(text)
        engine = GameEngine(board)
        controller = GameController(engine)
        printer = PrintBoard(self._output)
        has_printed = False

        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned or "Board:" in cleaned or "Commands:" in cleaned:
                continue

            if cleaned.startswith("wait"):
                wait_time = int(cleaned.split()[1])
                engine.advance_time(wait_time)
            elif cleaned.startswith("print board"):
                printer.print(board)
                has_printed = True
            elif cleaned.startswith("jump"):
                parts = cleaned.split()
                if len(parts) >= 3:
                    controller.handle_jump(int(parts[1]), int(parts[2]))
            elif cleaned.startswith("click"):
                parts = cleaned.split()
                if len(parts) >= 3:
                    controller.handle_click(int(parts[1]), int(parts[2]))

        if not has_printed:
            engine.force_all_moves()
            printer.print(board)
