# import pytest
# import io
# from main import main
# from rules import is_legal_rook_move, is_legal_king_move
# from board import Board
# from piece import Piece

# def test_rook_legal_move_horizontal_and_vertical():
#     """בדיקה שצריח יכול לנוע אופקית ואנכית במסלול פנוי."""
#     input_data = (
#         "Board:\n"
#         "wR . .\n"
#         ". . .\n"
#         "Commands:\n"
#         "click 50 50\n"
#         "click 250 50\n"
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert ". . wR" in output_stream.getvalue()

# def test_rook_move_blocked_by_piece():
#     """בדיקה שתנועת צריח נחסמת אם יש כלי באמצע המסלול."""
#     input_data = (
#         "Board:\n"
#         "wR wK .\n"
#         ". . .\n"
#         "Commands:\n"
#         "click 50 50\n"
#         "click 250 50\n"
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert "wR wK ." in output_stream.getvalue()

# def test_rook_capture_enemy():
#     """בדיקה שצריח יכול להכות כלי של היריב."""
#     input_data = (
#         "Board:\n"
#         "wR . bK\n"
#         ". . .\n"
#         "Commands:\n"
#         "click 50 50\n"
#         "click 250 50\n"
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert ". . wR" in output_stream.getvalue()

# def test_rook_illegal_diagonal_move_ignored():
#     """בדיקה שתנועה באלכסון לצריח היא לא חוקית."""
#     input_data = (
#         "Board:\n"
#         "wR . .\n"
#         ". . .\n"
#         "Commands:\n"
#         "click 50 50\n"
#         "click 150 150\n"
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert "wR . ." in output_stream.getvalue()

# def test_king_legal_and_illegal_moves_including_switch():
#     """כיסוי שורות 70-84: בדיקת מלך, החלפת בחירה של מלך, ותנועה לא חוקית."""
#     input_data = (
#         "Board:\n"
#         "wK wR .\n"
#         ". . .\n"
#         "Commands:\n"
#         "click 50 50\n"    # בחירת מלך
#         "click 250 50\n"   # תנועה לא חוקית (2 צעדים) - יתעלם
#         "click 150 50\n"   # לחיצה על כלי ידידותי (wR) - יחליף בחירה ל-wR!
#         "click 150 150\n"  # הזזת ה-wR צעד אחד למטה (חוקי לצריח)
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert "wK . ." in output_stream.getvalue()

# def test_other_pieces_fallback_logic():
#     """כיסוי שורות 96-99: בדיקת לוגיקת ברירת המחדל לכלים שאינם מלך או צריח (למשל רגלי wP)."""
#     input_data = (
#         "Board:\n"
#         "wP bK .\n"
#         "wR . .\n"
#         "Commands:\n"
#         "click 50 50\n"    # בחירת wP
#         "click 50 150\n"   # לחיצה על כלי ידידותי wR -> יחליף בחירה
#         "click 50 50\n"    # בחירת wP מחדש
#         "click 250 50\n"   # תנועה חופשית של ה-wP (כי אין לו חוקים עדיין) ל-ריק
#         "print board\n"
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert ". bK wP" in output_stream.getvalue()

# def test_main_exception_handling_line_103():
#     """כיסוי שורה 103: גרימת חריגה בתוך ה-try של הקליק כדי לבדוק את ה-except."""
#     input_data = (
#         "Board:\n"
#         "wK . .\n"
#         "Commands:\n"
#         "click abc 50\n"   # ערך לא מספרי - יזרוק ValueError וייקלע ל-except pass
#     )
#     input_stream = io.StringIO(input_data)
#     output_stream = io.StringIO()
#     main(input_stream=input_stream, output_stream=output_stream)
#     assert "wK . ." in output_stream.getvalue()
# def test_rook_and_king_edge_cases_for_coverage():
#     """כיסוי שורות חסרות ב-rules.py (תנועה לאותו מקום וחסימות בכיוון הפוך)."""
#     board = Board(3, 3)
#     board.set_piece(0, 0, Piece('w', 'R'))
#     board.set_piece(0, 2, Piece('w', 'R'))
    
#     # תנועה לאותו מקום (from == to)
#     assert is_legal_rook_move(board, 0, 0, 0, 0) is False
#     assert is_legal_king_move(0, 0, 0, 0) is False
    
#     # תנועה אופקית ואנכית בכיוון הפוך (מלמעלה למטה / מימין לשמאל) עם חסימה
#     board.set_piece(1, 0, Piece('w', 'K'))
#     assert is_legal_rook_move(board, 2, 0, 0, 0) is False # חסום מלמטה למעלה
#     assert is_legal_rook_move(board, 0, 2, 0, 0) is False # חסום מימין לשמאל 
import pytest
import io
from main import main
from rules import is_legal_bishop_move, is_legal_knight_move
from board import Board
from piece import Piece

def test_bishop_blocking_and_capture():
    """בדיקה שרץ נחסם על ידי כלי בדרך, אך יכול להכות אויב בסוף מסלול פנוי."""
    board = Board(3, 3)
    board.set_piece(0, 0, Piece('w', 'B'))
    board.set_piece(1, 1, Piece('w', 'P')) # חסימה ידידותית
    assert is_legal_bishop_move(board, 0, 0, 2, 2) is False

    # מסלול פנוי עם אויב בסופו
    board.set_piece(1, 1, None)
    board.set_piece(2, 2, Piece('b', 'P'))
    assert is_legal_bishop_move(board, 0, 0, 2, 2) is True

def test_knight_jumping_over_pieces():
    """בדיקה שפרש יכול לקפוץ מעל כלים חוסמים בהצלחה."""
    board = Board(3, 3)
    board.set_piece(0, 0, Piece('w', 'N'))
    board.set_piece(1, 0, Piece('w', 'P')) # כלי חוסם ישירות מלפניו
    board.set_piece(0, 1, Piece('b', 'R')) # כלי חוסם מצדדיו
    
    # תנועת L חוקית ל- (2,1)
    assert is_legal_knight_move(board, 0, 0, 2, 1) is True

def test_missing_controller_and_edge_cases():
    """טסטים כלליים לשמירה על כיסוי גבוה."""
    from controller import render_board
    b = Board(2, 2)
    assert ". .\n. ." in render_board(b)

    input_data = (
        "Board:\n"
        "wN . .\n"
        ". . .\n"
        "Commands:\n"
        "click 150 50\n" # קליק על ריק כששום דבר לא נבחר
        "click 50 50\n"  # בחירת פרש
        "click 150 150\n" # תנועה לא חוקית לפרש
    )
    main(input_stream=io.StringIO(input_data), output_stream=io.StringIO())   