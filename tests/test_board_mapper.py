import pytest
import io
from board_mapper import BoardMapper, InvalidCoordinatesError
from board import Board
from main import main

def test_board_mapper_correct_conversion():
    """בדיקה שפיקסלים מומרים בצורה נכונה לשורות ועמודות."""
    board = Board(width=8, height=8)
    mapper = BoardMapper(board)
    
    # x=150 (עמודה 1), y=250 (שורה 2)
    row, col = mapper.to_cell(x=150, y=250)
    assert row == 2
    assert col == 1

    # לחיצה בקצוות של משבצת 0,0
    row, col = mapper.to_cell(x=50, y=50)
    assert row == 0
    assert col == 0

def test_board_mapper_out_of_bounds_raises_error():
    """בדיקה שלחיצה מחוץ לגבולות הלוח זורקת שגיאה מתאימה."""
    board = Board(width=8, height=8)
    mapper = BoardMapper(board)
    
    with pytest.raises(InvalidCoordinatesError):
        mapper.to_cell(x=850, y=200)
        
    with pytest.raises(InvalidCoordinatesError):
        mapper.to_cell(x=-10, y=100)

def test_main_engine_click_and_move():
    """בדיקה אינטגרטיבית שהמנוע מזהה פקודות קליק ומזיז כלי."""
    input_data = (
        "Board:\n"
        "wK . .\n"
        ". . .\n"
        "Commands:\n"
        "click 50 50\n"    # בחירת המלך ב-(0,0)
        "click 150 50\n"   # הזזה ל-(0,1)
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = (
        ". wK .\n"
        ". . ."
    )
    assert output_stream.getvalue().strip() == expected

def test_main_engine_click_empty_and_switch_selection():
    """בדיקת מקרי קצה: לחיצה על ריק, והחלפת בחירה בין כלים."""
    input_data = (
        "Board:\n"
        "wR . wK\n"
        ". . .\n"
        "Commands:\n"
        "click 150 50\n"   # לחיצה על תא ריק כשאין בחירה (התעלמות)
        "click 50 50\n"    # בחירת ה-wR
        "click 50 50\n"    # לחיצה חוזרת על אותו כלי
        "click 250 50\n"   # החלפת בחירה ל-wK
        "click 250 150\n"  # הזזת ה-wK ל-(1,2)
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = (
        "wR . .\n"
        ". . wK"
    )
    assert output_stream.getvalue().strip() == expected

def test_main_engine_click_outside_ignored():
    """בדיקה שלחיצה מחוץ לגבולות הלוח או פקודה לא תקינה נתפסת ומתעלמים ממנה."""
    input_data = (
        "Board:\n"
        "wK . .\n"
        "Commands:\n"
        "click -10 50\n"   # מחוץ לגבולות (שלילי)
        "click 50 50\n"    # בחירה
        "click 500 50\n"   # מחוץ לגבולות (גדול מדי)
        "click 150\n"      # פקודה קצרה מדי (פורמט לא חוקי)
    )
    input_stream = io.StringIO(input_data)
    output_stream = io.StringIO()
    main(input_stream=input_stream, output_stream=output_stream)
    
    expected = "wK . ."
    assert output_stream.getvalue().strip() == expected