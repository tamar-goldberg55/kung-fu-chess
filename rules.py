"""Board-format validation rules."""

from typing import List

class BoardFormatError(ValueError):
    """Raised when raw board text violates the format contract."""

def validate_non_empty(rows: List[List[str]]) -> None:
    if not rows:
        raise BoardFormatError("Board must contain at least one row")

def validate_rectangular(rows: List[List[str]]) -> None:
    cleaned_rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    if not cleaned_rows: return
    widths = {len(row) for row in cleaned_rows}
    if len(widths) > 1:
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")

def is_target_occupied_by_pending(board, row, col):
    for move in board.pending_moves:
        if move['to_row'] == row and move['to_col'] == col:
            return True
    return False

def is_legal_rook_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    if from_row != to_row and from_col != to_col: return False
    if from_row == to_row and from_col == to_col: return False
    

    step_r = 0 if from_row == to_row else (1 if to_row > from_row else -1)
    step_c = 0 if from_col == to_col else (1 if to_col > from_col else -1)
    curr_r, curr_c = from_row + step_r, from_col + step_c
    while (curr_r != to_row or curr_c != to_col):
        if board.get_piece(curr_r, curr_c) is not None or is_target_occupied_by_pending(board, curr_r, curr_c):
            return False
        curr_r += step_r
        curr_c += step_c
    return True

def is_legal_bishop_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    if from_row == to_row and from_col == to_col: return False # תיקון
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    if row_diff != col_diff or row_diff == 0: return False
    row_step = 1 if to_row > from_row else -1
    col_step = 1 if to_col > from_col else -1
    curr_r, curr_c = from_row + row_step, from_col + col_step
    while curr_r != to_row:
        if board.get_piece(curr_r, curr_c) is not None or is_target_occupied_by_pending(board, curr_r, curr_c):
            return False
        curr_r += row_step
        curr_c += col_step
    return True

def is_legal_knight_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    if from_row == to_row and from_col == to_col: return False # תיקון
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

def is_legal_king_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    if from_row == to_row and from_col == to_col: return False # תיקון
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    return (row_diff <= 1 and col_diff <= 1) and not (row_diff == 0 and col_diff == 0)

def is_legal_pawn_move(board, from_row, from_col, to_row, to_col):
    if from_row == to_row and from_col == to_col: return False # תיקון
    piece = board.get_piece(from_row, from_col)
    direction = -1 if piece.color == 'w' else 1
    start_row = board.height - 1 if piece.color == 'w' else 0
    
    # תנועה קדימה (משבצת אחת)
    if from_col == to_col and to_row == from_row + direction:
        # כאן הבדיקה הקריטית: האם המשבצת ריקה סטטית וגם אין אף כלי שמתכנן להגיע לשם ב-pending_moves
        is_static_free = board.get_piece(to_row, to_col) is None
        is_pending_free = not is_target_occupied_by_pending(board, to_row, to_col)
        return is_static_free and is_pending_free

    # תנועה כפולה (2 משבצות) מהשורה ההתחלתית של הרגלי בלבד
    if from_col == to_col and from_row == start_row and to_row == from_row + 2 * direction:
        mid_row = from_row + direction
        mid_clear = (
            board.get_piece(mid_row, to_col) is None
            and not is_target_occupied_by_pending(board, mid_row, to_col)
        )
        dest_clear = (
            board.get_piece(to_row, to_col) is None
            and not is_target_occupied_by_pending(board, to_row, to_col)
        )
        return mid_clear and dest_clear
    
    # הכאה (אלכסון)
    if abs(from_col - to_col) == 1 and to_row == from_row + direction:
        target = board.get_piece(to_row, to_col)
        return target is not None and target.color != piece.color
        
    return False

def is_legal_queen_move(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
    if from_row == to_row and from_col == to_col: return False # תיקון
    return (
        is_legal_rook_move(board, from_row, from_col, to_row, to_col)
        or is_legal_bishop_move(board, from_row, from_col, to_row, to_col)
    )
MOVE_VALIDATORS = {
    'R': is_legal_rook_move,
    'B': is_legal_bishop_move,
    'N': is_legal_knight_move,
    'K': is_legal_king_move,
    'P': is_legal_pawn_move,
    'Q': is_legal_queen_move
}

