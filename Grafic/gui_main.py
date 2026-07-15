"""Graphical entry point for Kung Fu Chess."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board import Board, GameEngine
from Grafic.default_board import create_standard_board
from Grafic.display_coords import enable_windows_dpi_awareness, map_mouse_to_image
from Grafic.event_bridge import GfxEventBridge
from Grafic.game_snapshot import GameSnapshotBuilder
from Grafic.gfx_controller import GfxController
from Grafic.grafic_config import WINDOW_TITLE
from Grafic.observers.move_log_observer import MoveLogObserver
from Grafic.observers.score_observer import ScoreObserver
from Grafic.piece_state_manager import PieceStateManager
from Grafic.renderer import Renderer
from Grafic.sprite_manager import SpriteManager
from Grafic.window_mapper import WindowMapper


class GuiApp:
    """Main graphical application loop."""

    def __init__(self, board: Board | None = None, board_width: int = 8, board_height: int = 8):
        self.board = board if board is not None else create_standard_board(board_width, board_height)
        self.engine = GameEngine(self.board)
        self.piece_states = PieceStateManager(self.engine)
        self.sprite_manager = SpriteManager()
        self.renderer = Renderer(self.sprite_manager, self.piece_states)
        self.score_observer = ScoreObserver()
        self.move_log_observer = MoveLogObserver(self.board.height)
        self.event_bridge = GfxEventBridge(self.piece_states, self.score_observer, self.move_log_observer)
        self.engine.add_listener(self.event_bridge)

        offset_x, offset_y = self.renderer.board_offset
        self.window_mapper = WindowMapper(
            self.board.width,
            self.board.height,
            board_offset_x=offset_x,
            board_offset_y=offset_y,
        )
        self.controller = GfxController(self.engine, self.window_mapper, self.piece_states)
        self.snapshot_builder = GameSnapshotBuilder(
            self.engine,
            self.controller,
            self.piece_states,
            self.sprite_manager,
            self.score_observer.state,
            self.move_log_observer.state,
        )
        self._last_tick = time.time()
        self._image_width, self._image_height = self.renderer.canvas_size(
            self.board.width,
            self.board.height,
        )

    def run(self) -> None:
        enable_windows_dpi_awareness()
        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WINDOW_TITLE, self._on_mouse)

        while True:
            now = time.time()
            delta_ms = max(1, int((now - self._last_tick) * 1000))
            self._last_tick = now
            self.engine.advance_time(delta_ms)
            self.piece_states.update(delta_ms)
            self._render_frame()

            key = cv2.waitKey(16) & 0xFF
            if key in (ord("q"), 27):
                break

        cv2.destroyAllWindows()

    def _render_frame(self) -> None:
        snapshot = self.snapshot_builder.build()
        frame = self.renderer.render(snapshot, self.snapshot_builder)
        display = frame.img
        if display.ndim == 3 and display.shape[2] == 4:
            display = cv2.cvtColor(display, cv2.COLOR_BGRA2BGR)
        cv2.imshow(WINDOW_TITLE, display)

    def _on_mouse(self, event, x, y, _flags, _param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            click_time_ms = int(time.time() * 1000)
            image_x, image_y = self._map_click_to_image(x, y)
            self.controller.handle_click(image_x, image_y, click_time_ms)
            self._render_frame()
            cv2.waitKey(1)

    def _map_click_to_image(self, window_x: int, window_y: int) -> tuple[int, int]:
        try:
            image_rect = cv2.getWindowImageRect(WINDOW_TITLE)
        except cv2.error:
            return window_x, window_y
        return map_mouse_to_image(
            window_x,
            window_y,
            image_rect,
            self._image_width,
            self._image_height,
        )


def main() -> None:
    GuiApp().run()


if __name__ == "__main__":
    main()
