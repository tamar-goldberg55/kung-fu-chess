"""Configuration constants for the graphical layer."""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BOARD_IMAGE = ASSETS_DIR / "board.png"
PIECES_DIR = ASSETS_DIR / "pieces2"

CELL_SIZE = 100
SIDE_PANEL_WIDTH = 240
HEADER_HEIGHT = 70
FOOTER_HEIGHT = 50

WHITE_PLAYER_NAME = "WHITEPLAYER"
BLACK_PLAYER_NAME = "BLACKPLAYER"

DOUBLE_CLICK_MS = 450
LONG_REST_MS = 3000
SHORT_REST_MS = 2000

PIECE_NAMES = {
    "K": "King",
    "Q": "Queen",
    "R": "Rook",
    "B": "Bishop",
    "N": "Knight",
    "P": "Pawn",
}

PIECE_SCORES = {
    "P": 1,
    "N": 3,
    "B": 3,
    "R": 5,
    "Q": 9,
    "K": 0,
}

WINDOW_TITLE = "Kung Fu Chess"
