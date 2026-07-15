"""Tests for graphical window coordinate mapping."""

import pytest

from board_mapper import InvalidCoordinatesError
from Grafic.grafic_config import CELL_SIZE, HEADER_HEIGHT, SIDE_PANEL_WIDTH
from Grafic.window_mapper import WindowMapper


def test_click_maps_to_board_cell_with_offset():
    mapper = WindowMapper(8, 8)

    board_x = SIDE_PANEL_WIDTH + 2 * CELL_SIZE + 10
    board_y = HEADER_HEIGHT + 3 * CELL_SIZE + 10
    row, col = mapper.to_cell(board_x, board_y)

    assert (row, col) == (3, 2)


def test_click_maps_white_pawn_start_square():
    mapper = WindowMapper(8, 8)
    # white pawn e2 is row 6, col 4
    image_x = SIDE_PANEL_WIDTH + 4 * CELL_SIZE + 50
    image_y = HEADER_HEIGHT + 6 * CELL_SIZE + 50
    row, col = mapper.to_cell(image_x, image_y)
    assert (row, col) == (6, 4)


def test_click_outside_board_raises():
    mapper = WindowMapper(8, 8)

    with pytest.raises(InvalidCoordinatesError):
        mapper.to_cell(10, 10)
