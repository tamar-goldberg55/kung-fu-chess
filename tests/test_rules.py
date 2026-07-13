import pytest
from rules import is_legal_bishop_move, is_legal_knight_move
from board import Board
from piece import Piece
from rules import BoardFormatError, validate_non_empty, validate_rectangular
import io
from main import main


def test_validate_non_empty_rejects_empty_list():
    with pytest.raises(BoardFormatError):
        validate_non_empty([])


def test_validate_non_empty_accepts_non_empty_list():
    validate_non_empty([["wK", "."]])  # should not raise


def test_validate_rectangular_accepts_uniform_rows():
    rows = [["wK", ".", "."], [".", "wR", "."], [".", ".", "bK"]]
    validate_rectangular(rows)  # should not raise


def test_validate_rectangular_rejects_ragged_rows():
    rows = [["wK", "."], [".", "wR", "."]]
    with pytest.raises(BoardFormatError):
        validate_rectangular(rows)


def test_validate_rectangular_accepts_single_row():
    validate_rectangular([["wK", ".", "bK"]])  # should not raise

def test_full_rules_coverage():
    b = Board(3, 3)
    # בדיקת רץ
    b.set_piece(0, 0, Piece('w', 'B'))
    assert is_legal_bishop_move(b, 0, 0, 1, 1) is True # תנועה חוקית
    assert is_legal_bishop_move(b, 0, 0, 0, 1) is False # תנועה לא באלכסון
    
    # בדיקת פרש
    b.set_piece(0, 0, Piece('w', 'N'))
    assert is_legal_knight_move(b, 0, 0, 2, 1) is True # תנועת L
    assert is_legal_knight_move(b, 0, 0, 1, 1) is False # תנועה לא חוקית  

def test_main_error_handling():
    # קלט שגורם לשגיאת פורמט (מפעיל את ה-except ב-main)
    input_data = "Board:\nINVALID_ROW_WIDTH\n" 
    output = io.StringIO()
    main(input_stream=io.StringIO(input_data), output_stream=output)
    assert "ERROR" in output.getvalue()    

def test_game_over_on_king_capture():
    board = Board(3, 3)
    # נניח שצריח מלבן כובש מלך משחור
    board.set_piece(0, 0, Piece.from_token("wR"))
    board.set_piece(0, 2, Piece.from_token("bK"))
    
    # הוספת מהלך של לכידה
    board.pending_moves.append({
        'piece': board.get_piece(0, 0),
        'from_row': 0, 'from_col': 0,
        'to_row': 0, 'to_col': 2,
        'arrival_time': 100
    })
    
    board.process_time(100)
    assert board.game_over is True    