"""Pure-strategy PBE enumeration, with exact closed belief intervals.

The receiver has one action per observed signal, not one action per type.
A pure sender strategy specifies an action for EACH private type.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from models import ACTIONS, SIGNALS, TYPES, Game, homework_game


@dataclass(frozen=True)
class Interval:
    low: Fraction = Fraction(0)
    high: Fraction = Fraction(1)

    def contains(self, value):
        return self.low <= value <= self.high

    def intersect(self, other):
        lo, hi = max(self.low, other.low), min(self.high, other.high)
        return Interval(lo, hi) if lo <= hi else None


def receiver_payoffs(game: Game, signal: str, belief: Fraction):
    """belief means P(x | observed signal). Returns EU(u), EU(d)."""
    return {a: belief * game.payoff("x", signal, a, 1)
            + (1 - belief) * game.payoff("y", signal, a, 1) for a in ACTIONS}


def best_responses(game, signal, belief):
    values = receiver_payoffs(game, signal, belief)
    return tuple(a for a in ACTIONS if values[a] == max(values.values()))


def optimal_beliefs(game, signal, action):
    """Solve b*Δx + (1-b)*Δy >= 0, intersected with 0 <= b <= 1.

Weak inequalities preserve ties: either pure action is allowed at indifference.
None represents the empty set, not an arbitrary chosen posterior.
"""
    other = "d" if action == "u" else "u"
    dx = game.payoff("x", signal, action, 1) - game.payoff("x", signal, other, 1)
    dy = game.payoff("y", signal, action, 1) - game.payoff("y", signal, other, 1)
    slope = dx - dy
    if slope == 0:
        return Interval() if dy >= 0 else None
    threshold = -dy / slope
    if slope > 0:
        return Interval(max(Fraction(0), threshold), Fraction(1)) if threshold <= 1 else None
    return Interval(Fraction(0), min(Fraction(1), threshold)) if threshold >= 0 else None


def bayes_belief(game, sender, signal):
    mass_x = game.prior if sender[0] == signal else Fraction(0)
    mass_y = 1 - game.prior if sender[1] == signal else Fraction(0)
    return mass_x / (mass_x + mass_y) if mass_x + mass_y else None


@dataclass(frozen=True)
class Incentive:
    kind: str
    stay: Fraction
    deviate: Fraction

    @property
    def passes(self):
        return self.stay >= self.deviate


@dataclass(frozen=True)
class Candidate:
    sender: tuple[str, str]
    receiver: tuple[str, str]
    posteriors: dict[str, Fraction | None]
    beliefs: dict[str, Interval | None]
    incentives: tuple[Incentive, ...]

    @property
    def separating(self):
        return self.sender[0] != self.sender[1]

    @property
    def is_pbe(self):
        return all(b is not None for b in self.beliefs.values()) and all(i.passes for i in self.incentives)


def assess(game, sender, receiver):
    if len(sender) != 2 or any(s not in SIGNALS for s in sender):
        raise ValueError("Choose one signal for each sender type.")
    if len(receiver) != 2 or any(a not in ACTIONS for a in receiver):
        raise ValueError("Choose one receiver action after each signal.")
    responses = dict(zip(SIGNALS, receiver))
    posteriors, beliefs = {}, {}
    for signal in SIGNALS:
        posterior = bayes_belief(game, sender, signal)
        allowed = optimal_beliefs(game, signal, responses[signal])
        posteriors[signal] = posterior
        beliefs[signal] = (allowed.intersect(Interval(posterior, posterior))
                           if allowed is not None and posterior is not None else allowed)
    incentives = []
    for kind, signal in zip(TYPES, sender):
        other = "R" if signal == "L" else "L"
        incentives.append(Incentive(kind, game.payoff(kind, signal, responses[signal]),
                                     game.payoff(kind, other, responses[other])))
    return Candidate(tuple(sender), tuple(receiver), posteriors, beliefs, tuple(incentives))


def enumerate_candidates(game):
    # Explicit order makes the seminar's two separating cases appear first.
    senders = (("L", "R"), ("R", "L"), ("L", "L"), ("R", "R"))
    return [assess(game, s, r) for s in senders for r in product(ACTIONS, repeat=2)]


@dataclass(frozen=True)
class Refinement:
    supported: bool
    survives: bool | None
    explanation: str
    # For each unused signal, report each type's best possible deviation gain.
    gains: dict[str, dict[str, Fraction]]


def intuitive_criterion(game, candidate):
    """A deliberately scoped proof for the original homework, not a general IC solver.

No off-path signal => no belief restriction from this criterion.
Otherwise, if no type can STRICTLY gain even under its most favourable
receiver action, no type can make the profitable deviation required to reject
the equilibrium. This sufficient survival argument includes mixed responses,
since their payoff is a convex combination of the two pure-action payoffs.
"""
    original = homework_game()
    if game.prior != original.prior or game.payoffs != original.payoffs:
        return Refinement(False, None, "Intuitive Criterion for edited games is not implemented in v0.1. PBE analysis remains available.", {})
    candidate = assess(game, candidate.sender, candidate.receiver)
    if not candidate.is_pbe:
        return Refinement(True, None, "Not applicable: this candidate is not a PBE.", {})
    unused = [s for s in SIGNALS if s not in candidate.sender]
    if not unused:
        return Refinement(True, True, "Both signals are reached. There is no off-path signal on which the Intuitive Criterion can restrict beliefs.", {})
    gains = {s: {i.kind: max(game.payoff(i.kind, s, a) for a in ACTIONS) - i.stay
                 for i in candidate.incentives} for s in unused}
    if all(gain <= 0 for by_type in gains.values() for gain in by_type.values()):
        return Refinement(True, True, "Neither type can strictly gain from the unused signal under any receiver response. Indifference is not a profitable deviation, so this PBE survives.", gains)
    return Refinement(False, None, "This case needs a general refinement algorithm, which v0.1 does not implement.", gains)
