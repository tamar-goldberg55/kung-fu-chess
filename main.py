"""Entry point.

Reads a board fixture from standard input, parses + validates it, 
executes commands using polymorhipc rules, and prints the final state.
"""

import sys
from typing import TextIO

from controller import parse_board, render_board
from rules import BoardFormatError, MOVE_VALIDATORS
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
                            # שליפת פונקציית הבדיקה המתאימה לסוג הכלי מתוך המילון המרכזי
                            validator = MOVE_VALIDATORS.get(selected_piece.kind)
                            
                            if validator is not None:
                                is_legal = validator(board, selected_pos[0], selected_pos[1], row, col)
                                is_friendly = piece is not None and piece.color == selected_piece.color
                                
                                if is_legal and not is_friendly:
                                    # תנועה חוקית (למשבצת ריקה או הכאת אויב)
                                    board.set_piece(selected_pos[0], selected_pos[1], None)
                                    board.set_piece(row, col, selected_piece)
                                    selected_piece = None
                                    selected_pos = None
                                elif is_friendly:
                                    # לחיצה על כלי ידידותי - מחליפה את הבחירה אליו
                                    selected_piece = piece
                                    selected_pos = (row, col)
                            else:
                                # לוגיקת ברירת מחדל לכלים שעוד לא מופו במילון (תנועה חופשית)
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
                        pass

        # 3. הדפסת הלוח הסופי
        print(render_board(board), file=output_stream)

    except (BoardFormatError, InvalidPieceTokenError) as e:
        print(str(e), file=output_stream)
    except Exception as e:
        print(str(e), file=output_stream)


if __name__ == "__main__":
    main()