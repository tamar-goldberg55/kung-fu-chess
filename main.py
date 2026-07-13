"""Entry point.

Reads a board fixture from standard input, parses + validates it, and
prints the canonical form to standard output. No prompts, no debug
text — VPL checks exact output.
"""

import sys
from typing import TextIO

from controller import parse_board, render_board


def main(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    """Read a fixture, parse it, and write its canonical form.

    input_stream/output_stream default to real stdin/stdout, but can be
    supplied by a caller (e.g. a test) via dependency injection instead
    of monkey-patching sys.stdin/sys.stdout at runtime.
    """
    text = input_stream.read()
    board = parse_board(text)
    print(render_board(board), file=output_stream)


if __name__ == "__main__":
    main()
