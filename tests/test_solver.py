from fractions import Fraction as F
from itertools import product
import random

import pytest

from models import ACTIONS, KEYS, Game, homework_game
from solver import (Interval, assess, bayes_belief, best_responses,
                    enumerate_candidates, intuitive_criterion, optimal_beliefs)


def test_exact_homework_equilibria_and_belief_families():
    candidates = enumerate_candidates(homework_game())
    assert len(candidates) == 16
    winners = {(c.sender, c.receiver): c for c in candidates if c.is_pbe}
    assert set(winners) == {
        (("L", "R"), ("u", "d")),
        (("R", "R"), ("u", "u")),
        (("R", "R"), ("d", "u")),
    }
    sep = winners[(("L", "R"), ("u", "d"))]
    assert sep.beliefs == {"L": Interval(F(1), F(1)), "R": Interval(F(0), F(0))}
    for action, bounds in (("u", Interval(F(1, 2), F(1))), ("d", Interval(F(0), F(1, 2)))):
        pool = winners[(("R", "R"), (action, "u"))]
        assert pool.beliefs == {"L": bounds, "R": Interval(F(1, 2), F(1, 2))}
        assert pool.posteriors["L"] is None
        assert all(i.passes for i in pool.incentives)


def test_reverse_separation_and_pooling_l_fail_for_y():
    game = homework_game()
    reverse = assess(game, ("R", "L"), ("d", "u"))
    assert all(b is not None for b in reverse.beliefs.values())
    assert reverse.incentives[1].stay == 0
    assert reverse.incentives[1].deviate == 1
    for receiver in product(ACTIONS, repeat=2):
        c = assess(game, ("L", "L"), receiver)
        assert not c.is_pbe
        assert not c.incentives[1].passes


def test_indifference_and_receiver_thresholds():
    g = homework_game()
    assert best_responses(g, "L", F(1, 2)) == ("u", "d")
    assert best_responses(g, "R", F(1, 3)) == ("u", "d")
    assert optimal_beliefs(g, "R", "u") == Interval(F(1, 3), F(1))
    c = assess(g, ("R", "R"), ("d", "u"))
    assert c.incentives[0].stay == c.incentives[0].deviate == 2
    assert c.is_pbe  # Weak incentive constraints are enough.


def test_intuitive_criterion_uses_best_possible_deviation_payoffs():
    game = homework_game()
    winners = [c for c in enumerate_candidates(game) if c.is_pbe]
    assert len(winners) == 3
    for c in winners:
        result = intuitive_criterion(game, c)
        assert result.supported and result.survives
        if not c.separating:
            assert result.gains == {"L": {"x": F(0), "y": F(-1)}}
        else:
            assert result.gains == {}
    assert intuitive_criterion(game, assess(game, ("L", "L"), ("u", "u"))).survives is None


def test_edited_game_and_prior_recalculate_without_claiming_refinement():
    original = homework_game()
    edited = Game(F(1, 4), original.payoffs)
    assert bayes_belief(edited, ("R", "R"), "R") == F(1, 4)
    assert not any(c.is_pbe and c.sender == ("R", "R") for c in enumerate_candidates(edited))
    c = assess(edited, ("L", "R"), ("u", "d"))
    assert c.is_pbe
    assert not intuitive_criterion(edited, c).supported
    payoffs = dict(original.payoffs)
    payoffs["y", "L", "u"] = (3, 0)
    changed = Game(F(1, 2), payoffs)
    assert not assess(changed, ("L", "R"), ("u", "d")).is_pbe
    assert not intuitive_criterion(changed, c).supported


@pytest.mark.parametrize("dx,dy,expected", [
    (0, 0, Interval()), (2, 2, Interval()), (-2, -2, None),
    (0, -2, Interval(F(1), F(1))), (-2, 0, Interval(F(0), F(0))),
    (3, 1, Interval()), (-3, -1, None),
    (2, -1, Interval(F(1, 3), F(1))), (-2, 1, Interval(F(0), F(1, 3))),
])
def test_interval_solver_degenerate_and_boundary_cases(dx, dy, expected):
    payoffs = {key: (0, 0) for key in KEYS}
    payoffs["x", "L", "u"] = (0, dx)
    payoffs["y", "L", "u"] = (0, dy)
    assert optimal_beliefs(Game(F(1, 2), payoffs), "L", "u") == expected


def test_random_edited_games_against_direct_payoff_comparisons():
    """An independent grid oracle catches sign errors in belief inequalities."""
    rng = random.Random(17)
    for _ in range(50):
        g = Game(F(rng.randint(1, 9), 10), {k: (rng.randint(-5, 5), rng.randint(-5, 5)) for k in KEYS})
        for c in enumerate_candidates(g):
            for s, action in zip(("L", "R"), c.receiver):
                interval = optimal_beliefs(g, s, action)
                other = "d" if action == "u" else "u"
                for b in (F(n, 20) for n in range(21)):
                    chosen = b*g.payoff("x", s, action, 1)+(1-b)*g.payoff("y", s, action, 1)
                    alternate = b*g.payoff("x", s, other, 1)+(1-b)*g.payoff("y", s, other, 1)
                    assert (interval is not None and interval.contains(b)) == (chosen >= alternate)
            if c.is_pbe:
                for s, a in zip(("L", "R"), c.receiver):
                    bounds = c.beliefs[s]
                    for b in (bounds.low, bounds.high):
                        assert a in best_responses(g, s, b)
                for t, s in zip(("x", "y"), c.sender):
                    actions = dict(zip(("L", "R"), c.receiver))
                    other = "R" if s == "L" else "L"
                    assert g.payoff(t, s, actions[s]) >= g.payoff(t, other, actions[other])


def test_all_indifferent_game_has_all_16_profiles():
    g = Game(F(2, 5), {key: (0, 0) for key in KEYS})
    assert all(c.is_pbe for c in enumerate_candidates(g))


@pytest.mark.parametrize("prior", [0, 1, -1, 2, "nan", "inf"])
def test_invalid_priors_rejected(prior):
    with pytest.raises(ValueError):
        Game(prior, homework_game().payoffs)


def test_invalid_payoffs_and_exact_decimals():
    with pytest.raises(ValueError):
        Game(.5, {})
    payoffs = dict(homework_game().payoffs)
    payoffs["x", "L", "u"] = ("nan", 0)
    with pytest.raises(ValueError):
        Game(.5, payoffs)
    payoffs["x", "L", "u"] = (.1, .2)
    assert Game(.3, payoffs).payoff("x", "L", "u") == F(1, 10)
