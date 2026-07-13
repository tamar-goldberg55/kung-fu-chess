"""BoardMapper: Maps screen pixel coordinates to pure logical board coordinates.

Strictly adheres to the Single Responsibility Principle (SRP) by managing 
ONLY pixel-to-cell transformations and coordinate adaptations.
"""

from board import Board

# הגדרת קבועים מקומיים לפי דרישות הפרויקט (ניתן להעביר ל-config בהמשך)
CELL_SIZE = 100


class InvalidCoordinatesError(ValueError):
    """Raised when pixel clicks fall outside the legal boundaries of the board."""


class BoardMapper:
    """Adapts continuous pixel coordinates into discrete board row and column indices."""

    def __init__(self, board: Board):
        self._board = board

    def to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Convert pixel (x, y) coordinates to board index (row, col).
        
        Raises InvalidCoordinatesError if the click is outside the board bounds.
        """
        # בדיקה שלילית (Negative Testing) - מחוץ לגבולות
        if x < 0 or y < 0:
            raise InvalidCoordinatesError(f"Coordinates cannot be negative: ({x}, {y})")
            
        # חישוב הגבולות המקסימליים בפיקסלים על פי גודל הלוח בפועל
        max_width_px = self._board.width * CELL_SIZE
        max_height_px = self._board.height * CELL_SIZE
        
        if x >= max_width_px or y >= max_height_px:
            raise InvalidCoordinatesError(
                f"Click ({x}, {y}) is out of board bounds ({max_width_px}x{max_height_px})"
            )

        # המרת הפיקסלים לאינדקסים (חלוקת ערך שלמים)
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        return row, col