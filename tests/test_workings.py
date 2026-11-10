"""Regression tests for the numbers taught on the first page."""
from fractions import Fraction as F
from models import homework_game, Game
from solver import assess, best_responses, optimal_beliefs
from workings import (homework_examples, original_refinement_proof,
                      receiver_affine_payoff, receiver_calculations, selected_steps)
from study_notes import simplified_payoff


def test_original_receiver_arithmetic_and_boundaries():
    game = homework_game()
    assert receiver_affine_payoff(game, 'R', 'u') == (F(0), F(2))
    assert receiver_affine_payoff(game, 'R', 'd') == (F(1), F(-1))
    assert receiver_affine_payoff(game, 'L', 'u') == (F(0), F(1))
    assert receiver_affine_payoff(game, 'L', 'd') == (F(1), F(-1))
    assert [simplified_payoff(game, s, a) for s,a in [('R','u'),('R','d'),('L','u'),('L','d')]] == [
        r'2\mu_{R}', r'1-\mu_{R}', r'\mu_{L}', r'1-\mu_{L}']
    assert best_responses(game, 'R', F(1,3)) == ('u','d')
    assert best_responses(game, 'L', F(1,2)) == ('u','d')
    assert optimal_beliefs(game, 'R', 'u').low == F(1,3)
    assert optimal_beliefs(game, 'L', 'u').low == F(1,2)


def test_reference_separating_pooling_and_refinement_working():
    e = homework_examples()
    good, reverse = e['separating_good'], e['separating_reverse']
    assert good.is_pbe and good.posteriors == {'L': F(1), 'R': F(0)}
    assert [(i.stay,i.deviate) for i in good.incentives] == [(F(1),F(0)),(F(1),F(0))]
    assert not reverse.is_pbe
    assert [(i.stay,i.deviate) for i in reverse.incentives] == [(F(2),F(2)),(F(0),F(1))]
    for key, low, high in [('pooling_r_u',F(1,2),F(1)), ('pooling_r_d',F(0),F(1,2))]:
        c=e[key]
        assert c.is_pbe and c.posteriors['R'] == F(1,2)
        assert (c.beliefs['L'].low,c.beliefs['L'].high) == (low,high)
        calculated=receiver_calculations(e['game'],c)
        assert (calculated['R'][0].expected,calculated['R'][1].expected) == (F(1),F(1,2))
    assert all(not c.is_pbe for c in e['pooling_l'])
    proof=original_refinement_proof()
    assert all(p.survives for p in proof.values())
    assert proof['pooling_r_u'].gains['L'] == {'x':F(0),'y':F(-1)}


def test_selected_working_recalculates_for_edited_game():
    original=homework_game()
    payoffs=dict(original.payoffs)
    payoffs['y','L','u']=(3,0)
    changed=Game(F(1,2),payoffs)
    c=assess(changed,('L','R'),('u','d'))
    steps=selected_steps(changed,c)
    assert len(steps)==6
    assert not steps[-1][1]
    assert c.incentives[1].deviate == 3
    assert receiver_affine_payoff(changed,'L','u') == (F(0),F(1))  # P2 payoff unchanged.
    payoffs['x','R','u']=(2,5)
    changed2=Game(F(1,2),payoffs)
    assert receiver_affine_payoff(changed2,'R','u') == (F(0),F(5))
