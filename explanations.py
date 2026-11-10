"""Small formatting helpers: economics stays in solver.py, prose lives here."""

from models import SIGNALS
from solver import receiver_payoffs


def number(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def interval_text(interval, symbol="b"):
    if interval is None:
        return "∅ (no admissible belief)"
    if interval.low == interval.high:
        return f"{symbol} = {number(interval.low)}"
    return f"{number(interval.low)} ≤ {symbol} ≤ {number(interval.high)}"


def sender_label(sender):
    return f"x → {sender[0]}, y → {sender[1]}"


def receiver_label(receiver):
    return f"after L → {receiver[0]}, after R → {receiver[1]}"


def receiver_working(game, signal, posterior):
    symbol = f"b_{signal}"
    lines = []
    for action in ("u", "d"):
        vx = number(game.payoff("x", signal, action, 1))
        vy = number(game.payoff("y", signal, action, 1))
        formula = f"EU₂({action} | {signal}) = {symbol} × ({vx}) + (1 − {symbol}) × ({vy})"
        if posterior is not None:
            formula += f" = {number(receiver_payoffs(game, signal, posterior)[action])}"
        lines.append(formula)
    return lines


def failure_reasons(candidate):
    reasons = []
    for signal in SIGNALS:
        if candidate.beliefs[signal] is None:
            reasons.append(f"After {signal}, the proposed receiver action is not optimal at any belief consistent with Bayes' rule.")
    for incentive in candidate.incentives:
        if not incentive.passes:
            reasons.append(f"Type {incentive.kind} gains by deviating: {number(incentive.deviate)} > {number(incentive.stay)}.")
    return reasons
