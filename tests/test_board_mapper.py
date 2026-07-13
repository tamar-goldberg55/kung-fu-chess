import pytest
from board_mapper import BoardMapper, InvalidCoordinatesError
from board import Board

def test_board_mapper_correct_conversion():
    """בדיקה שפיקסלים מומרים בצורה נכונה לשורות ועמודות."""
    # נניח לוח בגודל 8 על 8
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
    
    # לחיצה מעבר לרוחב הלוח (8 תאים * 100 פיקסלים = 800)
    with pytest.raises(InvalidCoordinatesError):
        mapper.to_cell(x=850, y=200)
        
    # לחיצה בקואורדינטות שליליות
    with pytest.raises(InvalidCoordinatesError):
        mapper.to_cell(x=-10, y=100)