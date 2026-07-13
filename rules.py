"""Board-format validation rules.

Important: these are *format* rules ("is this raw text well-formed?"),
not chess movement rules — movement rules do not exist yet in this
iteration. Keeping this separate from board.py and controller.py keeps
each module focused on a single responsibility (SRP).
"""

from typing import List


class BoardFormatError(ValueError):
    """Raised when raw board text violates the format contract."""


def validate_non_empty(rows: List[List[str]]) -> None:
    """A board fixture must contain at least one row."""
    if not rows:
        raise BoardFormatError("Board must contain at least one row")


def validate_rectangular(rows: List[List[str]]) -> None:
    """Every row must have the same number of cells."""
    # מסננים החוצה שורות ריקות לחלוטין (למשל כאלו שנוצרו מירידת שורה בסוף הקלט)
    cleaned_rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    
    # אם אין שורות בכלל אחרי הסינון, אין מה לבדוק
    if not cleaned_rows:
        return

    # מחשבים את האורכים של השורות הנקיות
    widths = {len(row) for row in cleaned_rows}
    
    if len(widths) > 1:
        # חשוב: ודאי שב-main.py או כאן מודפס "ERROR ROW_WIDTH_MISMATCH" כפי שטסט 5 דורש
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")
def is_legal_rook_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """חוקי הצריח: תנועה ישרה בלבד, ללא חסימות במסלול."""
    if from_row != to_row and from_col != to_col:
        return False
    if from_row == to_row and from_col == to_col:
        return False
        
    # בדיקת חסימות אופקיות
    if from_row == to_row:
        step = 1 if to_col > from_col else -1
        for c in range(from_col + step, to_col, step):
            if board.get_piece(from_row, c) is not None:
                return False
    # בדיקת חסימות אנכיות
    else:
        step = 1 if to_row > from_row else -1
        for r in range(from_row + step, to_row, step):
            if board.get_piece(r, from_col) is not None:
                return False
    return True


def is_legal_bishop_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """חוקי הרץ: תנועה באלכסון בלבד, ללא חסימות במסלול."""
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    
    # חייב להיות אלכסון מושלם ולא אותה משבצת
    if row_diff != col_diff or row_diff == 0:
        return False
        
    # קביעת כיוון הצעדים (+1 או -1)
    row_step = 1 if to_row > from_row else -1
    col_step = 1 if to_col > from_col else -1
    
    # סריקת המסלול האלכסוני לחיפוש חסימות
    curr_r = from_row + row_step
    curr_c = from_col + col_step
    while curr_r != to_row and curr_c != to_col:
        if board.get_piece(curr_r, curr_c) is not None:
            return False
        curr_r += row_step
        curr_c += col_step
        
    return True


def is_legal_knight_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """חוקי הפרש: תנועה בצורת L (2X1 או 1X2). מדלג מעל חסימות בשקט."""
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


def is_legal_king_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    """חוקי המלך: לכל היותר משבצת אחת לכל כיוון."""
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    
    if row_diff == 0 and col_diff == 0:
        return False
    return row_diff <= 1 and col_diff <= 1


# מילון החוקים המרכזי שמנקה את ה-if/else מהמיין
MOVE_VALIDATORS = {
    'R': is_legal_rook_move,
    'B': is_legal_bishop_move,
    'N': is_legal_knight_move,
    'K': is_legal_king_move
}

class BoardFormatError(Exception):
    """נזרק כאשר מבנה הלוח אינו תקין."""
    pass