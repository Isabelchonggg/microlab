"""Presentation regressions: formulas are typeset while solver values stay exact."""
from fractions import Fraction
from pathlib import Path
from streamlit.testing.v1 import AppTest
from models import homework_game
from solver import assess
from math_display import interval_tex, posterior_tex, tex_number, expected_tex


def test_latex_uses_fractions_subscripts_and_bayes():
    game = homework_game()
    pooling = assess(game, ('R','R'), ('u','u'))
    assert tex_number(Fraction(1, 2)) == r'\frac{1}{2}'
    assert interval_tex(pooling.beliefs['L'], 'L') == r'\frac{1}{2}\le \mu_{L}\le 1'
    assert posterior_tex(game,pooling,'R').endswith(r'=\frac{1}{2}')
    assert r'E[U_2(u\mid R)]' in expected_tex(game,'R','u')


def test_app_keeps_math_out_of_plain_text():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    assert not app.exception
    assert app.latex
    assert not app.code
    visible = '\n'.join(m.value for m in app.markdown if not m.value.startswith('<div style="position:relative'))
    for raw in ('μ_L','μ_R','b_L','b_R','1/2','\\mu','\\frac'):
        assert raw not in visible
