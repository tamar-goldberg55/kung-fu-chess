"""Map OpenCV window mouse coordinates to rendered image pixels."""

from __future__ import annotations

import sys
from typing import Tuple


def enable_windows_dpi_awareness() -> None:
    """Prevent Windows HiDPI scaling from desyncing mouse clicks from pixels."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def map_mouse_to_image(
    window_x: int,
    window_y: int,
    image_rect: Tuple[int, int, int, int],
    image_width: int,
    image_height: int,
) -> Tuple[int, int]:
    """Convert a window click into image pixel coordinates."""
    rect_x, rect_y, rect_w, rect_h = image_rect
    if rect_w <= 0 or rect_h <= 0:
        return window_x, window_y

    if rect_w == image_width and rect_h == image_height and rect_x == 0 and rect_y == 0:
        return window_x, window_y

    image_x = int((window_x - rect_x) * image_width / rect_w)
    image_y = int((window_y - rect_y) * image_height / rect_h)
    image_x = max(0, min(image_width - 1, image_x))
    image_y = max(0, min(image_height - 1, image_y))
    return image_x, image_y
