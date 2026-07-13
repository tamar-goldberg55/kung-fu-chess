"""Entry point.

Reads a board fixture from standard input, parses + validates it, 
executes commands (including Rook movement validation), and prints the final state.
"""

import sys
from typing import TextIO

from controller import parse_board, render_board
from rules import BoardFormatError, is_legal_rook_move
from piece import InvalidPieceTokenError


def main(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    """Read a fixture, parse it, run commands, and write output safely."""
    try:
        text = input_stream.read()
        
        # 1. פירסור הלוח הלוגי
        board = parse_board(text)
        
        # 2. לוגיקת הרצת פקודות
        lines = text.splitlines()
        commands_started = False
        selected_piece = None
        selected_pos = None

        for line in lines:
            cleaned = line.strip()
            if cleaned.startswith("Commands:"):
                commands_started = True
                continue
            if commands_started and cleaned.startswith("click"):
                parts = cleaned.split()
                if len(parts) == 3:
                    try:
                        x, y = int(parts[1]), int(parts[2])
                        
                        from board_mapper import BoardMapper
                        mapper = BoardMapper(board)
                        
                        row, col = mapper.to_cell(x, y)
                        piece = board.get_piece(row, col)
                        
                        if selected_piece is not None:
                            # אם נבחר צריח, נאכוף את חוקי התנועה, החסימה וההכאה שלו
                            if selected_piece.kind == 'R':
                                if is_legal_rook_move(board, selected_pos[0], selected_pos[1], row, col):
                                    # תנועה חוקית לצריח (משבצת ריקה או הכאת יריב)
                                    board.set_piece(selected_pos[0], selected_pos[1], None)
                                    board.set_piece(row, col, selected_piece)
                                    selected_piece = None
                                    selected_pos = None
                                else:
                                    # תנועה לא חוקית לצריח - נבדוק אם זו החלפת בחירה חוקית בכלי ידידותי
                                    if piece is not None and piece.color == selected_piece.color:
                                        selected_piece = piece
                                        selected_pos = (row, col)
                                    # אחרת, פשוט מתעלמים מהלחיצה הלא חוקית והמצב נשאר כמו שהוא
                            else:
                                # לוגיקת בחירה ותנועה חופשית עבור כלים שאינם צריח (לתמיכה בטסטים של איטרציה 2)
                                if piece is not None and piece.color == selected_piece.color:
                                    selected_piece = piece
                                    selected_pos = (row, col)
                                else:
                                    board.set_piece(selected_pos[0], selected_pos[1], None)
                                    board.set_piece(row, col, selected_piece)
                                    selected_piece = None
                                    selected_pos = None
                        elif piece is not None:
                            # בחירת כלי לראשונה
                            selected_piece = piece
                            selected_pos = (row, col)
                            
                    except Exception:
                        # לחיצות מחוץ ללוח נתפסות פה ומתעלמים מהן בשקט
                        pass

        # 3. הדפסת הלוח הסופי
        print(render_board(board), file=output_stream)

    except (BoardFormatError, InvalidPieceTokenError) as e:
        print(str(e), file=output_stream)
    except Exception as e:
        print(str(e), file=output_stream)


if __name__ == "__main__":
    main()