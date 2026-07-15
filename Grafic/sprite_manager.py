"""Loads sprite configs and returns animation frames via the Img class."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np

from Grafic.grafic_config import CELL_SIZE, PIECES_DIR
from Grafic.img import Img
from piece import Piece


class SpriteManager:
    """State-based sprite lookup for each piece type."""

    def __init__(self, pieces_dir: Path = PIECES_DIR, cell_size: int = CELL_SIZE):
        self._pieces_dir = pieces_dir
        self._cell_size = cell_size
        self._configs: Dict[str, Dict] = {}
        self._frame_cache: Dict[str, Img] = {}

    def piece_to_folder(self, piece: Piece) -> str:
        color_suffix = "W" if piece.color == "w" else "B"
        return f"{piece.kind}{color_suffix}"

    def get_frame(self, piece: Piece, state: str, elapsed_ms: int) -> Img:
        frames = self._sprite_paths(piece, state)
        if not frames:
            return self._blank_sprite()

        config = self._load_config(piece, state)
        graphics = config.get("graphics", {})
        fps = graphics.get("frames_per_sec", 6)
        is_loop = graphics.get("is_loop", True)

        if fps <= 0:
            frame_index = 0
        else:
            frame_index = int((elapsed_ms / 1000.0) * fps)
            if is_loop:
                frame_index %= len(frames)
            else:
                frame_index = min(frame_index, len(frames) - 1)

        cache_key = f"{self.piece_to_folder(piece)}:{state}:{frame_index}"
        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key]

        sprite = Img().read(
            frames[frame_index],
            size=(self._cell_size, self._cell_size),
            keep_aspect=True,
            interpolation=cv2.INTER_AREA,
        )
        self._frame_cache[cache_key] = sprite
        return sprite

    def _blank_sprite(self) -> Img:
        blank = Img()
        blank.img = np.zeros((self._cell_size, self._cell_size, 4), dtype=np.uint8)
        return blank

    def _load_config(self, piece: Piece, state: str) -> Dict:
        key = f"{self.piece_to_folder(piece)}:{state}"
        if key in self._configs:
            return self._configs[key]
        config_path = self._pieces_dir / self.piece_to_folder(piece) / "states" / state / "config.json"
        if not config_path.exists():
            self._configs[key] = {}
            return {}
        with config_path.open(encoding="utf-8") as handle:
            self._configs[key] = json.load(handle)
        return self._configs[key]

    def _sprite_paths(self, piece: Piece, state: str) -> List[Path]:
        sprites_dir = self._pieces_dir / self.piece_to_folder(piece) / "states" / state / "sprites"
        if not sprites_dir.exists():
            return []
        return sorted(sprites_dir.glob("*.png"), key=lambda path: int(path.stem))
