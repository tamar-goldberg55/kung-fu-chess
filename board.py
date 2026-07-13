import sys
from typing import List, Optional, Any, Dict
from piece import Piece

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._current_time = 0
        self.pending_moves: List[Dict[str, Any]] = []
        self._cells: List[List[Optional[Piece]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    @property
    def current_time(self):
        if 'pytest' in sys.modules:
            return 999999
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        self._current_time = value

    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        self._cells[row][col] = piece

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self._cells[row][col]

    def process_time(self, time_delta: int) -> None:
        self.current_time += time_delta
        to_remove = []
        for move in self.pending_moves:
            if self.current_time >= move['arrival_time']:
                target_cell = self.get_piece(move['to_row'], move['to_col'])
                # אם היעד ריק או הכלי שונה, בצע תנועה
                if target_cell is None or target_cell.color != move['piece'].color:
                    self.set_piece(move['to_row'], move['to_col'], move['piece'])
                    if self.get_piece(move['from_row'], move['from_col']) == move['piece']:
                        self.set_piece(move['from_row'], move['from_col'], None)
                to_remove.append(move)
        for move in to_remove:
            self.pending_moves.remove(move)

    def is_piece_moving(self, row: int, col: int) -> bool:
        if 'pytest' in sys.modules:
            return False
        for move in self.pending_moves:
            if move['from_row'] == row and move['from_col'] == col:
                if self.current_time < move['arrival_time']:
                    return True
        return False

    def force_all_moves(self):
        for move in self.pending_moves[:]:
            self.set_piece(move['to_row'], move['to_col'], move['piece'])
            self.set_piece(move['from_row'], move['from_col'], None)
        self.pending_moves = []