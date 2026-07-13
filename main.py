import sys
from typing import TextIO
from controller import parse_board, render_board
from rules import MOVE_VALIDATORS
from board_mapper import BoardMapper
 
def main(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    try:
        text = input_stream.read()
        board = parse_board(text)
        lines = text.splitlines()
        
        selected_piece = None
        selected_pos = None
        has_printed = False
 
        for line in lines:
            cleaned = line.strip()
            if not cleaned or "Board:" in cleaned or "Commands:" in cleaned:
                continue
 
            # חסימת פקודות אם המשחק הסתיים
            if board.game_over and (cleaned.startswith("click") or cleaned.startswith("jump")):
                continue
 
            if cleaned.startswith("wait"):
                wait_time = int(cleaned.split()[1])
                board.process_time(wait_time)
            
            elif cleaned.startswith("print board"):
                print(render_board(board), file=output_stream)
                has_printed = True
 
            elif cleaned.startswith("jump"):
                parts = cleaned.split()
                try:
                    x, y = int(parts[1]), int(parts[2])
                    mapper = BoardMapper(board)
                    row, col = mapper.to_cell(x, y)
                    board.start_jump(row, col)
                except Exception:
                    continue
 
            elif cleaned.startswith("click"):
                parts = cleaned.split()
                try:
                    x, y = int(parts[1]), int(parts[2])
                    mapper = BoardMapper(board)
                    row, col = mapper.to_cell(x, y)
                    piece = board.get_piece(row, col)
                    is_unselectable = board.is_piece_moving(row, col) or board.is_piece_airborne(row, col)
 
                    if selected_piece:
                        validator = MOVE_VALIDATORS.get(selected_piece.kind)
                        if validator and validator(board, selected_pos[0], selected_pos[1], row, col):
                            if not board.has_active_motion():
                                if piece is None or piece.color != selected_piece.color:
                                    board.pending_moves.append({
                                        'piece': selected_piece, 
                                        'from_row': selected_pos[0], 'from_col': selected_pos[1], 
                                        'to_row': row, 'to_col': col, 
                                        'arrival_time': board.current_time + 1000
                                    })
                                    selected_piece = selected_pos = None
                                elif not is_unselectable:
                                    selected_piece, selected_pos = piece, (row, col)
                                else:
                                    selected_piece = selected_pos = None
                        else:
                            selected_piece = piece if (piece and not is_unselectable) else None
                            selected_pos = (row, col) if (piece and not is_unselectable) else None
                    elif piece and not is_unselectable:
                        selected_piece, selected_pos = piece, (row, col)
                except: continue
        
        if not has_printed:
            board.force_all_moves()
            print(render_board(board), file=output_stream)
 
    except Exception as e:
        print(f"ERROR: {str(e)}", file=output_stream)
 
if __name__ == "__main__":
    main()






