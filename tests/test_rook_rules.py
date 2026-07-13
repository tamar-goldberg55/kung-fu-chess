import pytest
import io
from main import main

def test_rook_legal_move_horizontal_and_vertical():
    """בדיקה שצריח יכול לנוע אופקית ואנכית במסלול פנוי."""
    input_data = (
        "Board:\n"
        "wR . .\n"
        ". . .\n"
        ". . .\n"
        "Commands:\n"
        "click 50 50\n"    # בחירת הצריח ב-(0,0)
        "click 250 50\n"   # תנועה אופקית ל-(0,2)
        "click 250 50\n"   # בחירה מחדש ב-(0,2)
        "click 250 250\n"  # תנועה אנכית ל-(2,2)
        "print board\n"
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = (
        ". . .\n"
        ". . .\n"
        ". . wR"
    )
    assert output_stream.getvalue().strip() == expected

def test_rook_move_blocked_by_piece():
    """בדיקה שתנועת צריח נחסמת אם יש כלי באמצע המסלול (חסימה אופקית/אנכית)."""
    input_data = (
        "Board:\n"
        "wR wK .\n"
        ". . .\n"
        "Commands:\n"
        "click 50 50\n"    # בחירת הצריח ב-(0,0)
        "click 250 50\n"   # ניסיון תנועה ל-(0,2) - לא חוקי כי wK חוסם!
        "print board\n"
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    # הלוח צריך להישאר ללא שינוי כי התנועה חסומה
    expected = (
        "wR wK .\n"
        ". . ."
    )
    assert output_stream.getvalue().strip() == expected

def test_rook_capture_enemy():
    """בדיקה שצריח יכול להכות כלי של היריב אך נחסם מכלי שלו בשורת היעד."""
    input_data = (
        "Board:\n"
        "wR . bK\n"
        ". . .\n"
        "Commands:\n"
        "click 50 50\n"    # בחירת צריח לבן
        "click 250 50\n"   # הכאת המלך השחור ב-(0,2) - חוקי!
        "print board\n"
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = (
        ". . wR\n"
        ". . ."
    )
    assert output_stream.getvalue().strip() == expected

def test_rook_illegal_diagonal_move_ignored():
    """בדיקה שתנועה באלכסון לצריח היא לא חוקית והמערכת מתעלמת ממנה."""
    input_data = (
        "Board:\n"
        "wR . .\n"
        ". . .\n"
        "Commands:\n"
        "click 50 50\n"    # בחירת צריח לבן ב-(0,0)
        "click 150 150\n"  # ניסיון תנועה באלכסון ל-(1,1) - לא חוקי!
        "print board\n"
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = (
        "wR . .\n"
        ". . ."
    )
    assert output_stream.getvalue().strip() == expected