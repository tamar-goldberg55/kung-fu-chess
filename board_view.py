"""View Adapter: maps internal board state to a read-only DTO."""

from dataclasses import dataclass
from typing import List, Tuple

from board import Board
from config import CELL_SEPARATOR, EMPTY_CELL


@dataclass(frozen=True)
class BoardDTO:
    width: int
    height: int
    rows: Tuple[Tuple[str, ...], ...]


class BoardViewAdapter:
    """Converts Board model objects into DTOs and textual renderings."""

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
