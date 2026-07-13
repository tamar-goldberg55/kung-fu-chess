"""Piece: a small value-object representing a single chess piece.

Piece knows only its own color and kind. It knows nothing about the
board, coordinates, rendering, or movement rules.
"""

from config import VALID_COLORS, VALID_KINDS


class InvalidPieceTokenError(ValueError):
    """Raised when a two-character board token is not a legal piece."""


class Piece:
    """Immutable representation of one piece: color + kind."""

    __slots__ = ("color", "kind")

    def __init__(self, color: str, kind: str):
        self.color = color
        self.kind = kind

    @classmethod
    def from_token(cls, token: str) -> "Piece":
        """Parse a token like 'wK' or 'bP' into a Piece.

        Raises InvalidPieceTokenError if the token is not exactly two
        characters, or the color/kind are not recognized.
        """
        if len(token) != 2:
            raise InvalidPieceTokenError(f"Invalid piece token: '{token}'")

        color, kind = token[0], token[1]
        if color not in VALID_COLORS or kind not in VALID_KINDS:
            raise InvalidPieceTokenError(f"Invalid piece token: '{token}'")

        return cls(color, kind)

    def to_token(self) -> str:
        """Return the canonical two-character textual token."""
        return f"{self.color}{self.kind}"

    def __eq__(self, other):
        return (
            isinstance(other, Piece)
            and self.color == other.color
            and self.kind == other.kind
        )

    def __hash__(self):
        return hash((self.color, self.kind))

    def __repr__(self):
        return f"Piece({self.color!r}, {self.kind!r})"
