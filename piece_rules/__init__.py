from piece_rules.base import PieceMoveRule
from piece_rules.rook_rule import RookRule
from piece_rules.bishop_rule import BishopRule
from piece_rules.knight_rule import KnightRule
from piece_rules.king_rule import KingRule
from piece_rules.pawn_rule import PawnRule
from piece_rules.queen_rule import QueenRule

RULE_REGISTRY = {
    "R": RookRule(),
    "B": BishopRule(),
    "N": KnightRule(),
    "K": KingRule(),
    "P": PawnRule(),
    "Q": QueenRule(),
}

__all__ = [
    "PieceMoveRule",
    "RookRule",
    "BishopRule",
    "KnightRule",
    "KingRule",
    "PawnRule",
    "QueenRule",
    "RULE_REGISTRY",
]
