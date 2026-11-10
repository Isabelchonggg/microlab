"""Streamlit study notes. Calculations stay in solver.py and workings.py."""
import streamlit as st
from explanations import receiver_label, sender_label
from models import ACTIONS, SIGNALS, homework_game
from solver import intuitive_criterion
from workings import homework_examples
from math_display import (belief_stages, equation, expected_tex, incentive_stages,
                          interval_tex, posterior_tex, receiver_stages, tex_number)


def render_selected_working(game, candidate):
    st.markdown('### ✏️ The Maths Behind the Game')
    st.caption('These workings follow the strategy and payoffs selected above.')
    identity = (game.prior, tuple(game.payoffs.items()), candidate.sender, candidate.receiver)
    if st.session_state.get('working_identity') != identity:
        st.session_state.working_identity = identity
        st.session_state.working_stage = 0
        st.session_state.working_final_revealed = False
    controls=st.columns([1,1,2])
    if controls[0].button('Show me the working ♡',type='primary',width='stretch'):
        st.session_state.working_stage=min(6,st.session_state.working_stage+1)
    if controls[1].button('Try it myself',width='stretch'):
        st.session_state.working_stage=0
        st.session_state.working_final_revealed=False
    hidden=controls[2].toggle('Hide the final answer until I reveal it',value=True,key='hide_working_final')
    if st.session_state.working_stage>=6 and hidden and not st.session_state.working_final_revealed:
        if st.button('Reveal my conclusion ♡'):
            st.session_state.working_final_revealed=True
    stage=st.session_state.working_stage
    st.progress(stage/6,text=f'{stage} of 6 working steps revealed')
    if stage==0:
        st.info('Choose a profile and reveal the first step when you’re ready.')
        return
    if stage>=1:
        with st.container(border=True):
            st.markdown('#### 1 · Proposed strategy')
            st.write(f'Player 1: {sender_label(candidate.sender)}. Player 2: {receiver_label(candidate.receiver)}.')
            st.write('Separating' if candidate.separating else 'Pooling')
    if stage>=2:
        st.markdown('#### 2 · Beliefs')
        for signal in SIGNALS:
            belief_stages(game,candidate,signal)
    if stage>=3:
        st.markdown('#### 3 · Expected payoffs')
        st.write('Expected utility means the average payoff Player 2 expects, weighted by the chance of each type.')
        for signal in SIGNALS:
            for action in ACTIONS:
                receiver_stages(game,signal,action,candidate.posteriors[signal])
    if stage>=4:
        st.markdown('#### 4 · Player 2’s best responses')
        for signal,action in zip(SIGNALS,candidate.receiver):
            equation(interval_tex(candidate.beliefs[signal],signal),
                     caption=f'Beliefs supporting action {action} after {signal}',tone='lavender')
            st.write(f'After {signal}, action {action} is optimal for these beliefs. At a boundary, both actions may be optimal.')
    if stage>=5:
        st.markdown('#### 5 · Player 1’s incentive constraints')
        for incentive in candidate.incentives:
            incentive_stages(incentive)
    if stage>=6:
        st.markdown('#### 6 · Conclusion')
        if hidden and not st.session_state.working_final_revealed:
            st.info('Conclusion hidden. Decide for yourself, then reveal it above.')
        else:
            equation(r'\boxed{\text{Pure-strategy PBE}}' if candidate.is_pbe else
                     r'\boxed{\text{Not a PBE}}',caption='Final result',
                     tone='mint' if candidate.is_pbe else 'coral')
            st.write('All belief, receiver and sender checks pass.' if candidate.is_pbe else
                     'At least one belief, receiver or sender check fails.')


def render_reference_notes(game):
    original=homework_game()
    reference=homework_examples()
    st.markdown('### Study cards · original Seminar 3 question')
    if game != original:
        st.warning('These cards use the original payoffs. The live workings above use your edited game.')
    with st.expander('① Strategies and equilibrium conditions'):
        equation(r'\text{Separating: }s_1(x)\ne s_1(y)\qquad\text{Pooling: }s_1(x)=s_1(y)',tone='pink')
        st.write('The sender chooses a signal for each private type. A separating strategy uses different signals; a pooling strategy uses the same one.')
        equation(r'U_1(\mathrm{stay}\mid t)\ge U_1(\mathrm{deviate}\mid t),\quad t\in\{x,y\}',tone='pink')
        st.write('The inequality means each type earns at least as much by following the proposed strategy as by switching signals.')
    with st.expander('② Beliefs and Bayesian probabilities'):
        equation(r'\mu_s=P(x\mid s),\quad s\in\{L,R\}',tone='lavender')
        st.write('The Greek letter mu is a belief: the probability that Player 1 is type x after Player 2 sees the signal shown in its subscript. The vertical bar means “given”.')
        equation(r'P(x\mid s)=\frac{P(s\mid x)P(x)}{P(s\mid x)P(x)+P(s\mid y)P(y)}',tone='lavender')
        st.write('Bayes’ rule applies when the signal occurs with positive probability. An unexpected signal has an off-path belief, which must support Player 2’s action.')
        equation(r'P(x)=\frac{1}{2}',caption='Nature’s prior in the original question',tone='lavender')
    with st.expander('③ Expected payoffs and best responses'):
        equation(r'E[U_2(a\mid s)]=\mu_s U_2(x,s,a)+(1-\mu_s)U_2(y,s,a)',tone='blue')
        st.write('The capital E means “expected”: Player 2 averages the two possible payoffs using the belief after the observed signal.')
        for signal in SIGNALS:
            st.markdown(f'**After {signal}**')
            for action in ACTIONS:
                equation(expected_tex(original,signal,action),tone='blue')
    with st.expander('④ Separating equilibrium working'):
        for name,key in (('Candidate A','separating_good'),('Candidate B','separating_reverse')):
            c=reference[key]
            st.markdown(f'**{name}: {sender_label(c.sender)}; {receiver_label(c.receiver)}**')
            for signal in SIGNALS:
                belief_stages(original,c,signal)
            for incentive in c.incentives:
                incentive_stages(incentive)
            st.success('Separating PBE') if c.is_pbe else st.error('This candidate is not a PBE.')
    with st.expander('⑤ Pooling equilibrium working'):
        for key in ('pooling_r_u','pooling_r_d'):
            c=reference[key]
            st.markdown(f'**{sender_label(c.sender)}; {receiver_label(c.receiver)}**')
            for signal in SIGNALS:
                belief_stages(original,c,signal)
            for incentive in c.incentives:
                incentive_stages(incentive)
        st.write('At the boundary belief, either pure response after the unexpected signal is optimal.')
        equation(r'\mu_L=\frac{1}{2}',tone='lavender')
    with st.expander('⑥ Intuitive Criterion'):
        st.write('The Intuitive Criterion checks whether a type could strictly benefit from an unexpected signal under any receiver response. It restricts beliefs about who would deviate.')
        c=reference['pooling_r_u']
        result=intuitive_criterion(original,c)
        for incentive in c.incentives:
            gain=result.gains['L'][incentive.kind]
            equation(rf'\max_{{a\in\{{u,d\}}}} U_1({incentive.kind},L,a)-U_1({incentive.kind},R,u)={tex_number(gain)}',tone='pink')
        st.write('Neither type can strictly gain by switching to the unused signal. The pooling-on-R equilibrium survives. The separating equilibrium also survives because both signals are reached.')
    with st.expander('⑦ How to write this in an exam'):
        st.write('State the sender strategy and both receiver actions. Calculate beliefs using Bayes’ rule at reached signals, then compare Player 2’s expected payoffs. Check each sender type’s incentive constraint and state the equilibrium verdict. If asked, apply the Intuitive Criterion to an unused signal.')
        equation(r'\mu_s=P(x\mid s)',caption='Write the belief and explain its meaning',tone='lavender')
        equation(r'E[U_2(u\mid s)]\ge E[U_2(d\mid s)]',caption='Check the proposed receiver action',tone='blue')
        equation(r'U_1(\mathrm{stay}\mid t)\ge U_1(\mathrm{deviate}\mid t)',caption='Check each sender type',tone='pink')
        equation(r'\boxed{\text{State the PBE verdict and valid beliefs}}',caption='Final sentence',tone='mint')


def simplified_payoff(game, signal, action):
    """Return a LaTeX affine payoff for backwards-compatible study calculations."""
    from workings import receiver_affine_payoff
    intercept, slope = receiver_affine_payoff(game, signal, action)
    symbol = rf'\mu_{{{signal}}}'
    if slope == 0:
        return tex_number(intercept)
    term = symbol if abs(slope) == 1 else tex_number(abs(slope)) + symbol
    if intercept == 0:
        return term if slope > 0 else '-' + term
    return tex_number(intercept) + ('+' if slope > 0 else '-') + term
