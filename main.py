import sys
from typing import TextIO, List, Dict, Any
from controller import parse_board, render_board
from rules import BoardFormatError, MOVE_VALIDATORS
from piece import InvalidPieceTokenError
from board_mapper import BoardMapper

def main(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    try:
        text = input_stream.read()
        board = parse_board(text)
        lines = text.splitlines()
        
        current_time = 0
        pending_moves = []
        selected_piece = None
        selected_pos = None
        has_printed = False

        # פונקציית עזר לביצוע תנועות
        def apply_pending_moves(time_limit):
            for move in pending_moves[:]:
                if time_limit > move['arrival_time']:
                    board.set_piece(move['to_row'], move['to_col'], move['piece'])
                    board.set_piece(move['from_row'], move['from_col'], None)
                    pending_moves.remove(move)

        for line in lines:
            cleaned = line.strip()
            if not cleaned or "Board:" in cleaned or "Commands:" in cleaned:
                continue

            if cleaned.startswith("wait"):
                current_time += int(cleaned.split()[1])
            elif cleaned.startswith("print board"):
                apply_pending_moves(current_time) # עדכון לפני הדפסה
                print(render_board(board), file=output_stream)
                has_printed = True
            elif cleaned.startswith("click"):
                # ... (אותה לוגיקת קליק) ...
                parts = cleaned.split()
                try:
                    x, y = int(parts[1]), int(parts[2])
                    mapper = BoardMapper(board)
                    row, col = mapper.to_cell(x, y)
                    piece = board.get_piece(row, col)
                    if selected_piece:
                        validator = MOVE_VALIDATORS.get(selected_piece.kind)
                        if validator and validator(board, selected_pos[0], selected_pos[1], row, col):
                            if piece is None or piece.color != selected_piece.color:
                                pending_moves.append({'piece': selected_piece, 'from_row': selected_pos[0], 'from_col': selected_pos[1], 'to_row': row, 'to_col': col, 'arrival_time': current_time + 1000})
                                selected_piece = selected_pos = None
                            else: selected_piece, selected_pos = piece, (row, col)
                        else: selected_piece, selected_pos = piece, (row, col)
                    elif piece: selected_piece, selected_pos = piece, (row, col)
                except: continue
        
        # כאן התיקון: גם אם לא היה print board, מעדכנים תנועות לפני הדפסה סופית
        if not has_printed:
            apply_pending_moves(current_time + 1) # +1 כדי לתפוס תנועות שזמנן הגיע בדיוק עכשיו
            print(render_board(board), file=output_stream)

    except Exception as e:
        print(f"ERROR: {str(e)}", file=output_stream)

if __name__ == "__main__":
    main()