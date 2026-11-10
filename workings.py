"""Calculated study notes for MicroLab; no Streamlit imports.

These functions return mathematical data. The UI decides how to reveal it.
"""
from dataclasses import dataclass
from fractions import Fraction
from models import ACTIONS, SIGNALS, TYPES, Game, homework_game
from solver import (Candidate, assess, best_responses, enumerate_candidates,
                    intuitive_criterion, optimal_beliefs, receiver_payoffs)


@dataclass(frozen=True)
class ReceiverCalculation:
    signal: str
    action: str
    x_payoff: Fraction
    y_payoff: Fraction
    belief: Fraction | None
    expected: Fraction | None
    optimal: object


def receiver_calculations(game: Game, candidate: Candidate):
    """Return the two payoff substitutions at each information set."""
    result = {}
    for signal in SIGNALS:
        belief = candidate.posteriors[signal]
        values = receiver_payoffs(game, signal, belief) if belief is not None else None
        result[signal] = tuple(ReceiverCalculation(
            signal, action, game.payoff("x", signal, action, 1),
            game.payoff("y", signal, action, 1), belief,
            values[action] if values is not None else None,
            optimal_beliefs(game, signal, action)) for action in ACTIONS)
    return result


def receiver_affine_payoff(game: Game, signal: str, action: str):
    """EU = intercept + slope * μ, with μ = P(x | signal)."""
    intercept = game.payoff("y", signal, action, 1)
    slope = game.payoff("x", signal, action, 1) - intercept
    return intercept, slope


def homework_examples():
    """Reference examples derived from the original game's solver state."""
    game = homework_game()
    return {
        "game": game,
        "separating_good": assess(game, ("L", "R"), ("u", "d")),
        "separating_reverse": assess(game, ("R", "L"), ("d", "u")),
        "pooling_r_u": assess(game, ("R", "R"), ("u", "u")),
        "pooling_r_d": assess(game, ("R", "R"), ("d", "u")),
        "pooling_l": tuple(c for c in enumerate_candidates(game) if c.sender == ("L", "L")),
    }


def selected_steps(game: Game, candidate: Candidate):
    """Six progressive stages, all computed for the currently selected game."""
    calculations = receiver_calculations(game, candidate)
    return (
        ("Proposed strategy", {"sender": candidate.sender, "receiver": candidate.receiver}),
        ("Beliefs", {"posteriors": candidate.posteriors, "admissible": candidate.beliefs}),
        ("Expected payoffs", calculations),
        ("Best responses", {s: {
            a: optimal_beliefs(game, s, a) for a in ACTIONS} for s in SIGNALS}),
        ("Incentive constraints", candidate.incentives),
        ("Conclusion", candidate.is_pbe),
    )


def original_refinement_proof():
    examples = homework_examples()
    return {key: intuitive_criterion(examples["game"], examples[key])
            for key in ("separating_good", "pooling_r_u", "pooling_r_d")}
