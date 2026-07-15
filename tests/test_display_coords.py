"""Tests for display coordinate mapping."""

from Grafic.display_coords import map_mouse_to_image


def test_identity_mapping_when_window_matches_image():
    image_x, image_y = map_mouse_to_image(540, 670, (0, 0, 1040, 870), 1040, 870)
    assert (image_x, image_y) == (540, 670)


def test_scaled_mapping_when_window_is_smaller_than_image():
    image_x, image_y = map_mouse_to_image(100, 50, (0, 0, 520, 435), 1040, 870)
    assert (image_x, image_y) == (200, 100)


def test_mapping_accounts_for_image_offset_in_window():
    image_x, image_y = map_mouse_to_image(120, 80, (20, 10, 500, 400), 1000, 800)
    assert (image_x, image_y) == (200, 140)
