"""The game data. Fractions keep indifference thresholds mathematically exact."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from types import MappingProxyType
from typing import Mapping

TYPES = ("x", "y")
SIGNALS = ("L", "R")
ACTIONS = ("u", "d")
KEYS = tuple(product(TYPES, SIGNALS, ACTIONS))


def rational(value) -> Fraction:
    """Convert decimal input through text, avoiding binary floating-point noise."""
    return Fraction(str(value))


@dataclass(frozen=True)
class Game:
    prior: Fraction
    payoffs: Mapping[tuple[str, str, str], tuple[Fraction, Fraction]]

    def __post_init__(self):
        prior = rational(self.prior)
        if not 0 < prior < 1:
            raise ValueError("Version 0.1 requires 0 < P(x) < 1: both types must be possible.")
        if set(self.payoffs) != set(KEYS):
            raise ValueError("Supply exactly the eight (type, signal, action) payoff pairs.")
        converted = {}
        for key, pair in self.payoffs.items():
            if len(pair) != 2:
                raise ValueError("Each outcome needs two finite payoffs.")
            converted[key] = tuple(rational(v) for v in pair)
        object.__setattr__(self, "prior", prior)
        object.__setattr__(self, "payoffs", MappingProxyType(converted))

    def payoff(self, kind, signal, action, player=0):
        return self.payoffs[kind, signal, action][player]


def homework_game() -> Game:
    return Game(Fraction(1, 2), dict(zip(KEYS, (
        (1, 1), (2, 0), (2, 2), (0, 0),
        (0, 0), (0, 1), (1, 0), (1, 1),
    ))))
