"""Tests for discrete motion path helpers."""

from Grafic.motion_path import current_path_index, motion_path_cells, one_square_before


def test_rook_path_includes_every_square():
    path = motion_path_cells("R", 0, 0, 0, 3)
    assert path == [(0, 0), (0, 1), (0, 2), (0, 3)]


def test_pawn_path_is_start_and_destination():
    path = motion_path_cells("P", 6, 4, 4, 4)
    assert path == [(6, 4), (5, 4), (4, 4)]


def test_one_square_before_destination():
    assert one_square_before(7, 7, 7, 4) == (7, 5)


def test_current_path_index_steps_each_second():
    path = motion_path_cells("P", 6, 4, 4, 4)
    assert current_path_index(path, 0, 1000) == 0
    assert current_path_index(path, 1000, 1000) == 1
    assert current_path_index(path, 2500, 1000) == 2
