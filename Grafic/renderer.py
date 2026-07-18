"""Renders the full GUI canvas using only the Img class."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from Grafic.game_snapshot import GameSnapshot, GameSnapshotBuilder
from Grafic.grafic_config import (
    BLACK_PLAYER_NAME,
    BOARD_IMAGE,
    CELL_SIZE,
    FOOTER_HEIGHT,
    HEADER_HEIGHT,
    SIDE_PANEL_WIDTH,
    WHITE_PLAYER_NAME,
)
from Grafic.img import Img
from Grafic.piece_state_manager import PieceStateManager
from Grafic.sprite_manager import SpriteManager


class Renderer:
    """Draws board, animated pieces, score, and move logs."""

    def __init__(
        self,
        sprite_manager: SpriteManager,
        piece_states: PieceStateManager,
        board_image: Path = BOARD_IMAGE,
        cell_size: int = CELL_SIZE,
    ):
        self._sprite_manager = sprite_manager
        self._piece_states = piece_states
        self._cell_size = cell_size
        self._board_offset_x = SIDE_PANEL_WIDTH
        self._board_offset_y = HEADER_HEIGHT
        self._board_template = Img().read(board_image)

    @property
    def board_offset(self) -> Tuple[int, int]:
        return self._board_offset_x, self._board_offset_y

    def canvas_size(self, board_width: int, board_height: int) -> Tuple[int, int]:
        board_pixel_width = board_width * self._cell_size
        board_pixel_height = board_height * self._cell_size
        total_width = SIDE_PANEL_WIDTH * 2 + board_pixel_width
        total_height = HEADER_HEIGHT + board_pixel_height + FOOTER_HEIGHT
        return total_width, total_height

    def render(self, snapshot: GameSnapshot, builder: GameSnapshotBuilder) -> Img:
        width, height = self.canvas_size(snapshot.board_width, snapshot.board_height)
        canvas = Img()
        canvas.img = np.full((height, width, 4), (70, 70, 70, 255), dtype=np.uint8)

        self._draw_board(canvas, snapshot)
        self._draw_legal_moves(canvas, snapshot)
        self._draw_threatened_squares(canvas, snapshot)
        self._draw_click_feedback(canvas, snapshot)
        self._draw_pieces(canvas, snapshot, builder)
        self._draw_board_labels(canvas, snapshot)
        self._draw_header_footer(canvas, snapshot)
        self._draw_debug_text(canvas, snapshot)
        self._draw_footer_help(canvas, snapshot)
        self._draw_side_panels(canvas, snapshot)
        if snapshot.game_over:
            self._draw_game_over(canvas)
        return canvas

    def _draw_board(self, canvas: Img, snapshot: GameSnapshot) -> None:
        board_img = self._scaled_board(snapshot.board_width, snapshot.board_height)
        board_img.draw_on(canvas, self._board_offset_x, self._board_offset_y)

    def _scaled_board(self, board_width: int, board_height: int) -> Img:
        target_w = board_width * self._cell_size
        target_h = board_height * self._cell_size
        resized = Img()
        resized.img = cv2.resize(self._board_template.img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        if resized.img.ndim == 3 and resized.img.shape[2] == 3:
            resized.img = cv2.cvtColor(resized.img, cv2.COLOR_BGR2BGRA)
        return resized

    def _draw_pieces(self, canvas: Img, snapshot: GameSnapshot, builder: GameSnapshotBuilder) -> None:
        id_to_tracked = {tracked.piece_id: tracked for tracked in self._piece_states.pieces}
        for piece_view in snapshot.pieces:
            tracked = id_to_tracked.get(piece_view.piece_id)
            if tracked is None:
                continue
            sprite = builder.get_sprite_for_piece_view(tracked, piece_view.elapsed_state_ms)
            x = self._board_offset_x + int(piece_view.visual_col * self._cell_size)
            y = self._board_offset_y + int(piece_view.visual_row * self._cell_size)
            try:
                sprite.draw_on(canvas, x, y)
            except ValueError:
                pass
            if piece_view.is_selected:
                self._draw_selection(canvas, x, y)
            if piece_view.rest_remaining_ms > 0:
                self._draw_rest_timer(canvas, x, y, piece_view.rest_remaining_ms)

    def _draw_selection(self, canvas: Img, x: int, y: int) -> None:
        overlay = Img()
        overlay.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
        overlay.img[:, :, 1] = 255
        overlay.img[:, :, 2] = 255
        overlay.img[:, :, 3] = 90
        try:
            overlay.draw_on(canvas, x, y)
        except ValueError:
            pass

    def _draw_legal_moves(self, canvas: Img, snapshot: GameSnapshot) -> None:
        for row, col in snapshot.legal_moves:
            x = self._board_offset_x + col * self._cell_size
            y = self._board_offset_y + row * self._cell_size
            overlay = Img()
            overlay.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
            overlay.img[:, :, 1] = 255
            overlay.img[:, :, 3] = 130
            try:
                overlay.draw_on(canvas, x, y)
            except ValueError:
                pass

            cx = x + self._cell_size // 2 - 8
            cy = y + self._cell_size // 2 + 8
            canvas.put_text("o", cx, cy, 0.9, color=(0, 220, 0), thickness=2)

    def _draw_threatened_squares(self, canvas: Img, snapshot: GameSnapshot) -> None:
        for row, col in snapshot.threatened_squares:
            x = self._board_offset_x + col * self._cell_size
            y = self._board_offset_y + row * self._cell_size
            overlay = Img()
            overlay.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
            overlay.img[:, :, 0] = 60
            overlay.img[:, :, 1] = 140
            overlay.img[:, :, 2] = 255
            overlay.img[:, :, 3] = 110
            try:
                overlay.draw_on(canvas, x, y)
            except ValueError:
                pass
            canvas.put_text("JUMP", x + 8, y + self._cell_size // 2 + 5, 0.4, color=(255, 220, 0), thickness=1)

    def _draw_click_feedback(self, canvas: Img, snapshot: GameSnapshot) -> None:
        if snapshot.last_click_pos is None:
            return
        row, col = snapshot.last_click_pos
        x = self._board_offset_x + col * self._cell_size
        y = self._board_offset_y + row * self._cell_size
        overlay = Img()
        overlay.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
        overlay.img[:, :, 1] = 200
        overlay.img[:, :, 3] = 70
        try:
            overlay.draw_on(canvas, x, y)
        except ValueError:
            pass

    def _draw_rest_timer(self, canvas: Img, x: int, y: int, remaining_ms: int) -> None:
        overlay = Img()
        overlay.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
        overlay.img[:, :, 0] = 80
        overlay.img[:, :, 1] = 80
        overlay.img[:, :, 2] = 220
        overlay.img[:, :, 3] = 110
        try:
            overlay.draw_on(canvas, x, y)
        except ValueError:
            pass
        seconds = remaining_ms / 1000.0
        label = f"{seconds:.1f}s"
        tx = x + self._cell_size // 2 - 22
        ty = y + self._cell_size // 2 + 8
        canvas.put_text(label, tx, ty, 0.55, color=(255, 255, 255), thickness=2)

    def _draw_debug_text(self, canvas: Img, snapshot: GameSnapshot) -> None:
        status_x = self._board_offset_x + 10
        canvas.put_text(
            f"Active moves: {snapshot.active_moves}",
            status_x,
            20,
            0.55,
            color=(255, 255, 255),
            thickness=1,
        )
        canvas.put_text(
            snapshot.status_message,
            status_x,
            42,
            0.45,
            color=(200, 255, 200),
            thickness=1,
        )
        if snapshot.selected_pos is not None:
            row, col = snapshot.selected_pos
            canvas.put_text(
                f"Selected: ({row}, {col})",
                status_x + 300,
                20,
                0.55,
                color=(0, 255, 255),
                thickness=1,
            )
        if snapshot.last_click_pos is not None:
            row, col = snapshot.last_click_pos
            cx = self._board_offset_x + col * self._cell_size + self._cell_size // 2 - 5
            cy = self._board_offset_y + row * self._cell_size + self._cell_size // 2 + 5
            canvas.put_text("+", cx, cy, 0.6, color=(255, 0, 255), thickness=2)

    def _draw_footer_help(self, canvas: Img, snapshot: GameSnapshot) -> None:
        width, height = self.canvas_size(snapshot.board_width, snapshot.board_height)
        footer_y = height - 18
        if snapshot.selected_pos is None:
            help_text = "Step 1: click any piece (both colors can move)"
        else:
            help_text = "Step 2: click a GREEN square to move or capture"
        canvas.put_text(help_text, 20, footer_y, 0.55, color=(255, 255, 180), thickness=1)
        canvas.put_text(
            "1. לחצי על כלי   2. ריבוע ירוק   דאבל-קליק=קפיצה",
            width // 2 - 280,
            footer_y,
            0.5,
            color=(255, 255, 180),
            thickness=1,
        )

    def _draw_board_labels(self, canvas: Img, snapshot: GameSnapshot) -> None:
        for index in range(snapshot.board_width):
            file_label = chr(ord("a") + index)
            x = self._board_offset_x + index * self._cell_size + self._cell_size // 3
            top_y = self._board_offset_y - 12
            bottom_y = self._board_offset_y + snapshot.board_height * self._cell_size + 20
            canvas.put_text(file_label, x, top_y, 0.5, color=(255, 255, 255), thickness=1)
            canvas.put_text(file_label, x, bottom_y, 0.5, color=(255, 255, 255), thickness=1)

        for row in range(snapshot.board_height):
            rank = str(snapshot.board_height - row)
            y = self._board_offset_y + row * self._cell_size + self._cell_size // 2
            left_x = self._board_offset_x - 18
            right_x = self._board_offset_x + snapshot.board_width * self._cell_size + 8
            canvas.put_text(rank, left_x, y, 0.5, color=(255, 255, 255), thickness=1)
            canvas.put_text(rank, right_x, y, 0.5, color=(255, 255, 255), thickness=1)

    def _draw_header_footer(self, canvas: Img, snapshot: GameSnapshot) -> None:
        width, _ = self.canvas_size(snapshot.board_width, snapshot.board_height)
        canvas.put_text(f"Name: {WHITE_PLAYER_NAME}", 20, 28, 0.6, color=(255, 255, 255), thickness=1)
        canvas.put_text(f"Score: {snapshot.score.white}", 20, 55, 0.55, color=(255, 255, 255), thickness=1)

        black_name_x = width - SIDE_PANEL_WIDTH + 10
        canvas.put_text(f"Name: {BLACK_PLAYER_NAME}", black_name_x, 28, 0.6, color=(255, 255, 255), thickness=1)
        canvas.put_text(f"Score: {snapshot.score.black}", black_name_x, 55, 0.55, color=(255, 255, 255), thickness=1)

    def _draw_side_panels(self, canvas: Img, snapshot: GameSnapshot) -> None:
        panel_top = HEADER_HEIGHT + 5
        panel_height = snapshot.board_height * self._cell_size + 20
        self._draw_panel_background(canvas, 10, panel_top, SIDE_PANEL_WIDTH - 20, panel_height)
        self._draw_panel_background(
            canvas,
            SIDE_PANEL_WIDTH + snapshot.board_width * self._cell_size + 10,
            panel_top,
            SIDE_PANEL_WIDTH - 20,
            panel_height,
        )
        self._draw_move_table(canvas, 20, HEADER_HEIGHT + 15, "White", snapshot.move_log.white_moves)
        black_panel_x = SIDE_PANEL_WIDTH + snapshot.board_width * self._cell_size + 20
        self._draw_move_table(canvas, black_panel_x, HEADER_HEIGHT + 15, "Black", snapshot.move_log.black_moves)

    def _draw_panel_background(self, canvas: Img, x: int, y: int, w: int, h: int) -> None:
        overlay = Img()
        overlay.img = np.zeros((h, w, 4), dtype=np.uint8)
        overlay.img[:, :, :3] = 45
        overlay.img[:, :, 3] = 180
        try:
            overlay.draw_on(canvas, x, y)
        except ValueError:
            pass

    def _draw_move_table(self, canvas: Img, x: int, y: int, title: str, moves) -> None:
        canvas.put_text(title, x, y, 0.65, color=(255, 255, 255), thickness=2)
        canvas.put_text("Time", x, y + 28, 0.5, color=(200, 200, 200), thickness=1)
        canvas.put_text("Move", x + 70, y + 28, 0.5, color=(200, 200, 200), thickness=1)
        row_y = y + 50
        if not moves:
            canvas.put_text("...", x, row_y, 0.5, color=(160, 160, 160), thickness=1)
            return
        for time_text, move_text in moves[-10:]:
            canvas.put_text(time_text, x, row_y, 0.5, color=(255, 255, 255), thickness=1)
            canvas.put_text(move_text, x + 70, row_y, 0.45, color=(255, 255, 255), thickness=1)
            row_y += 24

    def _draw_game_over(self, canvas: Img) -> None:
        height, width = canvas.img.shape[:2]
        overlay = Img()
        overlay.img = np.zeros((height, width, 4), dtype=np.uint8)
        overlay.img[:, :, 3] = 120
        overlay.draw_on(canvas, 0, 0)
        canvas.put_text("GAME OVER", width // 2 - 120, height // 2, 1.2, color=(0, 0, 255), thickness=2)
