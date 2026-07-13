"""Configuration constants for board parsing and printing.

Kept separate from logic so business rules never hard-code magic
strings/characters directly (see project clean-code guidelines).
"""

EMPTY_CELL = "."
CELL_SEPARATOR = " "

VALID_COLORS = ("w", "b")
VALID_KINDS = ("K", "Q", "R", "B", "N", "P")
