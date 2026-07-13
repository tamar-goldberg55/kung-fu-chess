"""Entry point.

Reads a board fixture from standard input, parses + validates it, 
executes commands (including Rook and King movement validation), and prints the final state.
"""

import sys
from typing import TextIO

from controller import parse_board, render_board
from rules import BoardFormatError, is_legal_rook_move, is_legal_king_move
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
                            # אכיפת חוקי הצריח
                            if selected_piece.kind == 'R':
                                if is_legal_rook_move(board, selected_pos[0], selected_pos[1], row, col):
                                    board.set_piece(selected_pos[0], selected_pos[1], None)
                                    board.set_piece(row, col, selected_piece)
                                    selected_piece = None
                                    selected_pos = None
                                else:
                                    if piece is not None and piece.color == selected_piece.color:
                                        selected_piece = piece
                                        selected_pos = (row, col)
                            
                            # אכיפת חוקי המלך
                            elif selected_piece.kind == 'K':
                                # מלך יכול לנוע לריק או להכות יריב, בתנאי שהמרחק הוא מקסימום משבצת אחת
                                is_legal = is_legal_king_move(selected_pos[0], selected_pos[1], row, col)
                                is_friendly = piece is not None and piece.color == selected_piece.color
                                
                                if is_legal and not is_friendly:
                                    board.set_piece(selected_pos[0], selected_pos[1], None)
                                    board.set_piece(row, col, selected_piece)
                                    selected_piece = None
                                    selected_pos = None
                                elif is_friendly:
                                    # החלפת בחירה לכלי ידידותי אחר
                                    selected_piece = piece
                                    selected_pos = (row, col)
                                    
                            else:
                                # לוגיקת בחירה ותנועה חופשית עבור כלים אחרים שעוד לא מימשנו
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