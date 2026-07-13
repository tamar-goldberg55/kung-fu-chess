"""Entry point."""

import sys
from typing import TextIO

from controller import parse_board, render_board
from rules import BoardFormatError
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
                        
                        if piece is not None:
                            if selected_piece is not None and selected_pos == (row, col):
                                # לחיצה חוזרת על אותו כלי - נשאיר אותו נבחר או נתעלם
                                pass
                            elif selected_piece is not None:
                                # טסט 4: לחיצה על כלי אחר מחליפה את הבחירה!
                                selected_piece = piece
                                selected_pos = (row, col)
                            else:
                                # בחירת כלי לראשונה
                                selected_piece = piece
                                selected_pos = (row, col)
                        else:
                            # אם נלחץ תא ריק ויש כלי נבחר - נבצע תנועה (טסט 1)
                            if selected_piece is not None:
                                board.set_piece(selected_pos[0], selected_pos[1], None)
                                board.set_piece(row, col, selected_piece)
                                selected_piece = None
                                selected_pos = None
                            # טסט 2: אם נלחץ תא ריק ואין כלי נבחר - פשוט מתעלמים
                    except Exception:
                        # טסט 3: לחיצה מחוץ ללוח נזרקת כשגיאה ב-Mapper, פה אנחנו תופסים אותה ומתעלמים
                        pass

        # 3. הדפסת הלוח הסופי
        print(render_board(board), file=output_stream)

    except (BoardFormatError, InvalidPieceTokenError) as e:
        print(str(e), file=output_stream)
    except Exception as e:
        print(str(e), file=output_stream)


if __name__ == "__main__":
    main()