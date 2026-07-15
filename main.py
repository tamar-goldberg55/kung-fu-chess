import sys
from typing import TextIO

from text_test_runner import TextTestRunner


def main(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    try:
        TextTestRunner(input_stream, output_stream).run()
    except Exception as e:
        print(f"ERROR: {str(e)}", file=output_stream)


if __name__ == "__main__":
    main()
