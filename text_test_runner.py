"""Runs text-based game scenarios without a GUI."""

import sys
from typing import TextIO

from board_parser import parse_board
from game_controller import GameController
from game_engine import GameEngine
from print_board import PrintBoard


class TextTestRunner:
    """Simulates user input and terminal output for full game scenarios."""

    def __init__(self, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
        self._input = input_stream
        self._output = output_stream

    def run(self) -> None:
        text = self._input.read()
        board = parse_board(text)
        engine = GameEngine(board)
        controller = GameController(engine)
        printer = PrintBoard(self._output)
        has_printed = False

        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned or "Board:" in cleaned or "Commands:" in cleaned:
                continue

            if cleaned.startswith("wait"):
                wait_time = int(cleaned.split()[1])
                engine.advance_time(wait_time)
            elif cleaned.startswith("print board"):
                printer.print(board)
                has_printed = True
            elif cleaned.startswith("jump"):
                parts = cleaned.split()
                if len(parts) >= 3:
                    controller.handle_jump(int(parts[1]), int(parts[2]))
            elif cleaned.startswith("click"):
                parts = cleaned.split()
                if len(parts) >= 3:
                    controller.handle_click(int(parts[1]), int(parts[2]))

        if not has_printed:
            engine.force_all_moves()
            printer.print(board)
