"""Math typesetting and five-stage presentation; no equilibrium calculations."""
from fractions import Fraction
from itertools import count
_ids = count()
import streamlit as st
from solver import receiver_payoffs
from workings import receiver_affine_payoff


def tex_number(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    sign = '-' if value < 0 else ''
    return rf'{sign}\frac{{{abs(value.numerator)}}}{{{value.denominator}}}'


def belief(signal):
    return rf'\mu_{{{signal}}}'


def interval_tex(interval, signal):
    b = belief(signal)
    if interval is None:
        return rf'{b}\in\varnothing'
    if interval.low == interval.high:
        return rf'{b}={tex_number(interval.low)}'
    return rf'{tex_number(interval.low)}\le {b}\le {tex_number(interval.high)}'


def posterior_tex(game, candidate, signal):
    px = game.prior if candidate.sender[0] == signal else Fraction(0)
    py = 1-game.prior if candidate.sender[1] == signal else Fraction(0)
    if px+py == 0:
        return rf'{belief(signal)}=P(x\mid {signal})\quad\text{{off path}}'
    return rf'{belief(signal)}=\frac{{{tex_number(px)}}}{{{tex_number(px)}+{tex_number(py)}}}={tex_number(candidate.posteriors[signal])}'


def expected_tex(game, signal, action, posterior=None):
    ux = game.payoff('x',signal,action,1)
    uy = game.payoff('y',signal,action,1)
    b = belief(signal) if posterior is None else tex_number(posterior)
    return rf'E[U_2({action}\mid {signal})]={b}\cdot {tex_number(ux)}+(1-{b})\cdot {tex_number(uy)}'


def incentive_tex(incentive):
    op = r'\ge' if incentive.passes else '<'
    return rf'U_1(\mathrm{{stay}}\mid {incentive.kind})={tex_number(incentive.stay)}\;{op}\;{tex_number(incentive.deviate)}=U_1(\mathrm{{deviate}}\mid {incentive.kind})'


def equation(formula, *, caption=None, tone='black'):
    with st.container(border=True, key=f'math_{tone}_{next(_ids)}'):
        if caption:
            st.caption(caption)
        st.latex(formula)


def stages(title, general, substitute, simplify, result, intuition, *, tone='black', working_tone=None):
    st.markdown(f'**{title}**')
    working_tone = working_tone or tone
    for name, value, shade in (
        ('1 · General formula', general, 'black'),
        ('2 · Substitute values', substitute, working_tone),
        ('3 · Simplify', simplify, working_tone),
        ('4 · Final result', result, tone),
    ):
        equation(value, caption=name, tone=shade)
    with st.container(border=True, key=f'math_intuition_{next(_ids)}'):
        st.caption('5 · Economic intuition')
        st.write(intuition)


def receiver_stages(game, signal, action, posterior=None):
    ux=game.payoff('x',signal,action,1)
    uy=game.payoff('y',signal,action,1)
    b=belief(signal)
    intercept,slope=receiver_affine_payoff(game,signal,action)
    symbol=belief(signal) if posterior is None else tex_number(posterior)
    sign='+' if slope>=0 else '-'
    affine=rf'E[U_2({action}\mid {signal})]={tex_number(intercept)}{sign}{tex_number(abs(slope))}\cdot {symbol}'
    result=(rf'E[U_2({action}\mid {signal})]={tex_number(receiver_payoffs(game,signal,posterior)[action])}'
            if posterior is not None else affine)
    stages(f'Player 2 after {signal}: action {action}',
        rf'E[U_2({action}\mid {signal})]={b}U_2(x,{signal},{action})+(1-{b})U_2(y,{signal},{action})',
        expected_tex(game,signal,action),
        affine,
        result,
        f'Player 2 weights the payoff for each possible type by the belief after {signal}. '+
        ('The selected signal is reached, so Bayes’ rule fixes that belief.' if posterior is not None else
         'The signal is off path, so the belief remains a variable.'),tone='blue')


def belief_stages(game,candidate,signal):
    p=candidate.posteriors[signal]
    px=game.prior if candidate.sender[0]==signal else Fraction(0)
    py=1-game.prior if candidate.sender[1]==signal else Fraction(0)
    stages(f'Belief after {signal}',
        rf'{belief(signal)}=\frac{{P({signal}\mid x)P(x)}}{{P({signal})}}',
        rf'{belief(signal)}=\frac{{{tex_number(px)}}}{{{tex_number(px)}+{tex_number(py)}}}' if p is not None else
        rf'P({signal})={tex_number(px)}+{tex_number(py)}=0',
        posterior_tex(game,candidate,signal) if p is not None else rf'{belief(signal)}\in[0,1]',
        posterior_tex(game,candidate,signal) if p is not None else interval_tex(candidate.beliefs[signal],signal),
        f'The belief is the probability of type x after seeing {signal}. '+
        ('Bayes’ rule fixes it because this signal occurs. The denominator is the total chance of seeing that signal.' if p is not None else
         'This signal is unexpected; Player 2’s chosen response restricts the possible beliefs.'),tone='black')


def incentive_stages(incentive):
    stages(f'Player 1, type {incentive.kind}',
        rf'U_1(\mathrm{{stay}}\mid {incentive.kind})\ge U_1(\mathrm{{deviate}}\mid {incentive.kind})',
        rf'{tex_number(incentive.stay)}\ge {tex_number(incentive.deviate)}',
        incentive_tex(incentive),
        rf'\boxed{{\text{{{ "Satisfied" if incentive.passes else "Profitable deviation" }}}}}',
        'This type prefers its proposed signal or is indifferent.' if incentive.passes else
        'This type gains by switching signals, so the profile fails the sender incentive test.',
        tone='green' if incentive.passes else 'red', working_tone='red')
