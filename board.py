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
        # הערה: בטסטים רגילים אנחנו רוצים זמן אמיתי, לא קבוע
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
        sorted_moves = sorted(self.pending_moves, key=lambda m: m['arrival_time'])
        
        to_remove = []
        for move in sorted_moves:
            if self.current_time >= move['arrival_time']:
                # 1. ודא שהכלי עדיין בנקודת המוצא
                if self.get_piece(move['from_row'], move['from_col']) != move['piece']:
                    to_remove.append(move)
                    continue
                
                # 2. בדיקת חסימות לאורך כל המסלול (ל-Rook זה קריטי)
                # נשתמש ב-validator הקיים כדי לוודא שאין כלים בדרך
                from rules import MOVE_VALIDATORS
                validator = MOVE_VALIDATORS.get(move['piece'].kind)
                
                # אם המסלול חסום, התנועה מבוטלת
                if validator and not validator(self, move['from_row'], move['from_col'], move['to_row'], move['to_col']):
                    to_remove.append(move)
                    continue
 
                # 3. בדיקה שהיעד פנוי
                if self.get_piece(move['to_row'], move['to_col']) is None:
                    self.set_piece(move['to_row'], move['to_col'], move['piece'])
                    self.set_piece(move['from_row'], move['from_col'], None)
                
                to_remove.append(move)
        
        for move in to_remove:
            if move in self.pending_moves:
                self.pending_moves.remove(move)
 
    def is_piece_moving(self, row: int, col: int) -> bool:
        for move in self.pending_moves:
            if move['from_row'] == row and move['from_col'] == col:
                return True
        return False
 
    def has_active_motion(self) -> bool:
        """Common-route rule: only one motion may be in flight at a time,
        anywhere on the board, regardless of piece color. Used by the
        controller to reject a second move request while one is pending.
        """
        return bool(self.pending_moves)
 
    def force_all_moves(self):
        for move in self.pending_moves[:]:
            self.set_piece(move['to_row'], move['to_col'], move['piece'])
            self.set_piece(move['from_row'], move['from_col'], None)
        self.pending_moves = []

























