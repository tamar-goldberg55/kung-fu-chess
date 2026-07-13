from typing import List

from board import Board
from config import CELL_SEPARATOR, EMPTY_CELL
from piece import Piece
from rules import validate_non_empty, validate_rectangular, BoardFormatError


def _split_rows(text: str) -> List[List[str]]:
    """Split raw text into rows of whitespace-separated tokens.
    
    Supports both formal fixtures (with 'Board:' and 'Commands:') 
    and simple raw board strings used in local unit tests.
    """
    raw_lines = text.splitlines()
    
    # בדיקה: אם המילה "Board:" בכלל לא קיימת בטקסט, נפרסר את כל השורות הלא-ריקות
    if "Board:" not in text:
        return [line.split() for line in raw_lines if line.strip() != ""]

    # אם המילה "Board:" קיימת, נשתמש בלוגיקת הסינון המדויקת עבור הפיקסטור
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
    """Parse raw fixture text into a validated Board instance.

    Infers width/height from the text and validates:
      - at least one row exists
      - all rows have the same number of cells
      - every non-empty token is a legal piece token
    """
    raw_rows = _split_rows(text)
    
    # 1. בדיקה שהלוח אינו ריק
    validate_non_empty(raw_rows)
    
    # 2. בדיקה שכל השורות באותו אורך
    try:
        validate_rectangular(raw_rows)
    except BoardFormatError:
        raise BoardFormatError("ERROR ROW_WIDTH_MISMATCH")

    # 3. בדיקה של כל הטוקנים בלוח - לוודא שאין טוקן לא מוכר (כמו xZ או zZ)
    for row in raw_rows:
        for token in row:
            if token != EMPTY_CELL:
                try:
                    Piece.from_token(token)
                except Exception:
                    # מייבאים וזורקים את השגיאה הספציפית שהטסט המקומי מחפש, 
                    # אך עם הטקסט שהמערכת החיצונית מצפה לו
                    from piece import InvalidPieceTokenError
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


def render_board(board: Board) -> str:
    """Render a Board back into its canonical textual form."""
    lines = []
    for row_index in range(board.height):
        tokens = []
        for col_index in range(board.width):
            piece = board.get_piece(row_index, col_index)
            tokens.append(piece.to_token() if piece else EMPTY_CELL)
        lines.append(CELL_SEPARATOR.join(tokens))
    return "\n".join(lines)