"""Validation service for move legality."""

from dataclasses import dataclass
from typing import Optional

from piece import Piece
from piece_rules import RULE_REGISTRY
from rule_context import RuleContext


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    reason: Optional[str] = None


class RuleEngine:
    """Checks whether a piece may legally move to the requested target."""

    def validate(
        self,
        context: RuleContext,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        piece: Piece,
    ) -> ValidationResult:
        rule = RULE_REGISTRY.get(piece.kind)
        if rule is None:
            return ValidationResult(False, "unknown_piece_kind")
        if not rule.is_legal(context, from_row, from_col, to_row, to_col):
            return ValidationResult(False, "illegal_move")
        return ValidationResult(True)
