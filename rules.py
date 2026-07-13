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
    """מחזירה True אם תנועת הצריח ממשבצת המקור למשבצת היעד חוקית לחלוטין."""
    # 1. צריח חייב לנוע רק בשורה ישרה או בעמודה ישרה (לא באלכסון או תנועה מוזרה)
    if from_row != to_row and from_col != to_col:
        return False

    # 2. תנועה למקום הנוכחי היא לא מהלך חוקי
    if from_row == to_row and from_col == to_col:
        return False

    # 3. בדיקה שאין כלים שחוסמים את הדרך באמצע המסלול
    if from_row == to_row:  # תנועה אופקית (באותה שורה)
        step = 1 if to_col > from_col else -1
        for c in range(from_col + step, to_col, step):
            if board.get_piece(from_row, c) is not None:
                return False
    else:  # תנועה אנכית (באותה עמודה)
        step = 1 if to_row > from_row else -1
        for r in range(from_row + step, to_row, step):
            if board.get_piece(r, from_col) is not None:
                return False

    # 4. בדיקת משבצת היעד (מותר תא ריק, או כלי של היריב. אסור להכות כלי של עצמך)
    src_piece = board.get_piece(from_row, from_col)
    dest_piece = board.get_piece(to_row, to_col)
    
    if dest_piece is not None and src_piece is not None:
        if src_piece.color == dest_piece.color:
            return False  # חסימה על ידי כלי ידידותי

    return True