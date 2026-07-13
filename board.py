import sys
from typing import List, Optional, Any, Dict
from piece import Piece
 
class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._current_time = 0
        self.pending_moves: List[Dict[str, Any]] = []
        self.airborne_pieces: List[Dict[str, Any]] = []
        self._game_over = False
        self._cells: List[List[Optional[Piece]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
 
    @property
    def current_time(self):
        return self._current_time
 
    @current_time.setter
    def current_time(self, value):
        self._current_time = value
 
    @property
    def game_over(self) -> bool:
        return self._game_over
 
    def _check_king_capture(self, captured_piece: Optional[Piece]) -> None:
        """Marks the game as over if the piece being overwritten is a king."""
        if captured_piece is not None and captured_piece.kind == 'K':
            self._game_over = True
 
    def _check_pawn_promotion(self, row: int, col: int) -> None:
        """Promotes a pawn sitting on the last row of its travel to a queen."""
        piece = self.get_piece(row, col)
        if piece is None or piece.kind != 'P':
            return
        last_row = 0 if piece.color == 'w' else self.height - 1
        if row == last_row:
            self.set_piece(row, col, Piece(piece.color, 'Q'))
 
    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        self._cells[row][col] = piece
 
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self._cells[row][col]
 
    def is_piece_airborne(self, row: int, col: int) -> bool:
        """True while a piece at (row, col) is mid-jump (rules 1-2)."""
        return any(a['row'] == row and a['col'] == col for a in self.airborne_pieces)
 
    def start_jump(self, row: int, col: int) -> bool:
        """Starts a jump for the piece at (row, col)."""
        piece = self.get_piece(row, col)
        if piece is None:
            return False
        if self.is_piece_moving(row, col):
            return False
        if self.is_piece_airborne(row, col):
            return False
 
        self.airborne_pieces.append({
            'piece': piece,
            'row': row,
            'col': col,
            'land_time': self.current_time + 1000,
        })
        return True
 
    def _resolve_airborne_interception(self, move: Dict[str, Any]) -> bool:
        """Rule 3: if an enemy piece is airborne exactly at this move's
        destination, the airborne piece captures the arriving piece.
        """
        for airborne in self.airborne_pieces:
            if airborne['row'] == move['to_row'] and airborne['col'] == move['to_col']:
                if airborne['piece'].color != move['piece'].color:
                    self.airborne_pieces.remove(airborne)
                    return True
        return False
 
    def _apply_move(self, move: Dict[str, Any]) -> None:
        """Apply one already-due move to the board."""
        if self._resolve_airborne_interception(move):
            self.set_piece(move['from_row'], move['from_col'], None)
            return
 
        target = self.get_piece(move['to_row'], move['to_col'])
        if target is None or target.color != move['piece'].color:
            self._check_king_capture(target)
            self.set_piece(move['to_row'], move['to_col'], move['piece'])
            self.set_piece(move['from_row'], move['from_col'], None)
            self._check_pawn_promotion(move['to_row'], move['to_col'])
 
    def _land_airborne_pieces(self) -> None:
        self.airborne_pieces = [
            a for a in self.airborne_pieces if self.current_time < a['land_time']
        ]
 
    def process_time(self, time_delta: int) -> None:
        self.current_time += time_delta
        self.pending_moves.sort(key=lambda m: m['arrival_time'])
        
        to_remove = []
        for move in self.pending_moves:
            if self.current_time >= move['arrival_time']:
                self._apply_move(move)
                to_remove.append(move)
        
        for move in to_remove:
            if move in self.pending_moves:
                self.pending_moves.remove(move)
 
        self._land_airborne_pieces()
 
    def is_piece_moving(self, row: int, col: int) -> bool:
        for move in self.pending_moves:
            if move['from_row'] == row and move['from_col'] == col:
                return True
        return False
 
    def has_active_motion(self) -> bool:
        return len(self.pending_moves) > 0
 
    def force_all_moves(self):
        for move in self.pending_moves[:]:
            self._apply_move(move)
        self.pending_moves = []
        self.airborne_pieces = []






















