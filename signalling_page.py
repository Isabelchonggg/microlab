"""Single interactive Signalling Model page; solver and tree remain independent."""
import streamlit as st
from explanations import number, receiver_label, sender_label
from math_display import (belief_stages, equation, expected_tex, incentive_stages,
                          incentive_tex, interval_tex, posterior_tex, receiver_stages, tex_number)
from models import ACTIONS, KEYS, SIGNALS, Game, homework_game
from solver import assess, enumerate_candidates, intuitive_criterion, optimal_beliefs, receiver_payoffs
from visualization import game_tree

SENDERS = (('L','R'),('R','L'),('L','L'),('R','R'))


def _game_identity(game):
    return (game.prior, tuple(game.payoffs.items()))


def _clear_verification():
    st.session_state.pop('revealed_profile',None)
    st.session_state.pop('equilibrium_request',None)


def _show_equilibrium(game):
    sender=st.session_state.tree_sender
    winners=[c for c in enumerate_candidates(game) if c.sender==sender and c.is_pbe]
    st.session_state.equilibrium_request=(_game_identity(game),sender)
    st.session_state.pop('revealed_profile',None)
    if len(winners)==1:
        chosen=winners[0]
        st.session_state.tree_l,st.session_state.tree_r=chosen.receiver
        st.session_state.revealed_profile=(sender,chosen.receiver)
    elif len(winners)>1:
        manual=(st.session_state.tree_l,st.session_state.tree_r)
        if any(c.receiver==manual for c in winners):
            st.session_state.revealed_profile=(sender,manual)


def _use_equilibrium(sender,receiver):
    st.session_state.tree_l,st.session_state.tree_r=receiver
    st.session_state.revealed_profile=(sender,receiver)


def _show_equilibrium_result(game,sender,winners):
    if st.session_state.get('equilibrium_request')!=(_game_identity(game),sender):
        return
    st.markdown('#### Equilibrium check')
    if not winners:
        st.warning('No pure-strategy PBE supports this Player 1 candidate in the current game.')
        for c in enumerate_candidates(game):
            if c.sender!=sender:
                continue
            belief_ok=all(interval is not None for interval in c.beliefs.values())
            sender_ok=all(i.passes for i in c.incentives)
            st.write(f'{receiver_label(c.receiver)}: '+
                     ('receiver and Bayes checks pass' if belief_ok else 'receiver or Bayes check fails')+
                     '; '+('both sender incentives pass' if sender_ok else 'a sender incentive fails')+'.')
        return
    st.success(f'{len(winners)} receiver profile'+('s' if len(winners)!=1 else '')+
               ' support this candidate as a PBE. Belief intervals are shown below.')
    if len(winners)==1:
        st.caption('The unique supported receiver response was selected when you pressed Show equilibrium.')
    for index,c in enumerate(winners,1):
        with st.container(border=True):
            st.write(f'**Option {index}: {receiver_label(c.receiver)}**')
            for signal in SIGNALS:
                equation(interval_tex(c.beliefs[signal],signal),
                         caption=f'Valid belief after {signal}',tone='black')
            if st.session_state.get('revealed_profile')==(sender,c.receiver):
                st.caption('This option is highlighted in green on both game trees.')
            else:
                st.button(f'Use equilibrium option {index}',key=f'use_equilibrium_{index}',
                          on_click=_use_equilibrium,args=(sender,c.receiver))


def _reset():
    st.session_state.game=homework_game()
    st.session_state.editor_version=st.session_state.get('editor_version',0)+1
    _clear_verification()


def _render_criterion(game,candidate):
    st.markdown('#### 8 · Intuitive Criterion')
    if not candidate.is_pbe:
        st.write('The criterion refines an equilibrium. This profile is not a PBE, so it does not apply.')
        return
    result=intuitive_criterion(game,candidate)
    if not result.supported:
        st.info('A general Intuitive Criterion proof is not implemented for edited payoffs or this case. The PBE calculation above remains valid.')
        return
    st.write('The criterion checks whether a type could strictly benefit from an unused signal under any receiver action. Indifference does not count as a profitable deviation.')
    if result.gains:
        for signal,by_type in result.gains.items():
            for kind,gain in by_type.items():
                equation(rf'\max_{{a\in\{{u,d\}}}}U_1({kind},{signal},a)-U_1({kind},\mathrm{{equilibrium}})={tex_number(gain)}',
                         caption=f'Type {kind} switching to unused signal {signal}',tone='red')
    else:
        st.write('Both signals occur, so there is no unused signal on which to restrict beliefs.')
    if result.survives:
        equation(r'\boxed{\text{Survives the Intuitive Criterion}}',caption='Refined conclusion',tone='green')
    else:
        st.info(result.explanation)


FOCUS_OPTIONS = ('Overview','Beliefs','Expected utility','Receiver best responses',
                 'Sender incentive constraints','Equilibrium conclusion')


def _apply_tree_click(target,state=None):
    """Use the same state keys as the visible strategy controls."""
    if state is None:
        state=st.session_state
    parts=target.split(':')
    if parts[0]!='select':
        return False
    role=parts[1] if len(parts)>1 else ''
    if role=='terminal' and len(parts)==5:
        _,_,kind,signal,action=parts
        if kind not in ('x','y') or signal not in SIGNALS or action not in ACTIONS:
            return False
        sender=list(state['tree_sender'])
        sender[0 if kind=='x' else 1]=signal
        state['tree_sender']=tuple(sender)
        state['tree_l' if signal=='L' else 'tree_r']=action
        state['focus_kind'],state['focus_signal'],state['focus_action']=kind,signal,action
        state['math_focus']='Sender incentive constraints'
        state['tree_view_mode']='Trace one path'
        state['tree_click_notice']=(f'Tracing type {kind} → {signal} → {action}. The other type’s signal and the other information set’s response remain as selected.')
    elif role=='receiver' and len(parts)==5:
        _,_,kind,signal,action=parts
        if kind not in ('x','y') or signal not in SIGNALS or action not in ACTIONS:
            return False
        key='tree_l' if signal=='L' else 'tree_r'
        if state[key]==action and state.get('focus_kind')==kind and state.get('focus_signal')==signal and state.get('focus_action')==action:
            return False
        state[key]=action
        state['focus_kind'],state['focus_signal'],state['focus_action']=kind,signal,action
        state['math_focus']='Receiver best responses'
        state['tree_view_mode']='Trace one path'
        state['tree_click_notice']=(f'Player 2 now chooses {action} after {signal} at both nodes of that information set. '
                                    'The selected type’s path is traced; the other strategy choices are preserved.')
    elif role=='sender' and len(parts)==4 and parts[2] in ('x','y') and parts[3] in SIGNALS:
        _,_,first,choice=parts
        old=state['tree_sender']
        updated=(choice,old[1]) if first=='x' else (old[0],choice)
        state['tree_sender']=updated
        state['focus_kind'],state['focus_signal']=first,choice
        state['focus_action']=state['tree_l' if choice=='L' else 'tree_r']
        state['math_focus']='Sender incentive constraints'
        state['tree_view_mode']='Trace one path'
        state['tree_click_notice']=f'Type {first} now sends {choice}. Beliefs, payoffs, incentives and the PBE check have been recalculated.'
    else:
        return False
    state.pop('revealed_profile',None)
    state.pop('equilibrium_request',None)
    state['focus_compare_actions']=False
    state['tree_chart_version']=state.get('tree_chart_version',0)+1
    return True


def _select_math_focus(concept,signal=None,action=None,kind=None,compare=False):
    st.session_state.math_focus=concept
    st.session_state.focus_compare_actions=compare
    if signal is not None:
        st.session_state.focus_signal=signal
    if action is not None:
        st.session_state.focus_action=action
    if kind is not None:
        st.session_state.focus_kind=kind
        if signal is None and concept=='Sender incentive constraints':
            signal=st.session_state.tree_sender[0 if kind=='x' else 1]
            st.session_state.focus_signal=signal
            st.session_state.focus_action=st.session_state.tree_l if signal=='L' else st.session_state.tree_r
    st.session_state.tree_view_mode='Trace one path'


def _full_strategy():
    st.session_state.tree_view_mode='Full strategy'
    st.session_state.math_focus='Overview'


def _selected_tree_target(event,names):
    selection=event.get('selection',{}) if event else {}
    points=selection.get('points',[])
    for point in points:
        index=point.get('curve_number',point.get('curveNumber'))
        if isinstance(index,int) and 0<=index<len(names):
            name=names[index]
            if isinstance(name,str) and name.startswith('select:'):
                return name
    return None


def _on_tree_select(style):
    key=st.session_state.get(f'tree_active_chart_key_{style}')
    target=_selected_tree_target(st.session_state.get(key),
                                 st.session_state.get(f'tree_target_names_{style}',()))
    if target:
        _apply_tree_click(target)


def _on_rect_tree_select():
    _on_tree_select('rectangular')


def _on_branch_tree_select():
    _on_tree_select('branching')


def _focus_card(game,candidate,focus):
    concept=focus['concept']
    if concept=='Overview':
        st.write('Choose a mathematical card to connect its equation to the exact branches and payoffs above.')
        return
    signal=focus['signal']
    kind=focus['kind']
    action=focus['action']
    with st.container(border=True,key='math_focus_result'):
        st.markdown(f'**{concept} · visual focus**')
        if concept=='Beliefs':
            p=candidate.posteriors[signal]
            equation(posterior_tex(game,candidate,signal) if p is not None else
                     interval_tex(candidate.beliefs[signal],signal),
                     caption=f'Belief after {signal}',tone='black')
            st.write(f'The dotted {signal} information set joins both possible type nodes. '+
                     ('The red branches reaching it determine the Bayes numerator and denominator.' if p is not None else
                      'No selected sender branch reaches it, so Bayes’ rule does not pin down the belief. The displayed interval supports the selected receiver action.'))
        elif concept=='Expected utility':
            p=candidate.posteriors[signal]
            actions=ACTIONS if focus.get('compare_actions') else (action,)
            for evaluated in actions:
                equation(expected_tex(game,signal,evaluated,p),
                         caption=f'Player 2 evaluates action {evaluated} after {signal}',tone='blue')
                if p is not None:
                    equation(rf'E[U_2({evaluated}\mid {signal})]={tex_number(receiver_payoffs(game,signal,p)[evaluated])}',
                             caption='Calculated expected payoff',tone='blue')
            st.write(f'Look at both type-contingent payoff pairs after {signal}. '+
                     'Player 2 sees the signal, not the private type. A thick grey action branch means it is being evaluated but is not your selected response.')
        elif concept=='Receiver best responses':
            proposed=dict(zip(SIGNALS,candidate.receiver))[signal]
            for possible in ACTIONS:
                equation(interval_tex(optimal_beliefs(game,signal,possible),signal),
                         caption=f'Action {possible} is optimal after {signal}',tone='blue')
            if candidate.beliefs[signal] is None:
                st.warning(f'Your selected action {proposed} after {signal} is not a best response for a Bayes-consistent belief.')
            else:
                st.success(f'Your selected action {proposed} after {signal} is a best response for the displayed valid belief range.')
            st.write(f'The dotted {signal} information set connects both Player 2 nodes. The same selected action applies at both nodes.')
        elif concept=='Sender incentive constraints':
            i=next(i for i in candidate.incentives if i.kind==kind)
            chosen=dict(zip(('x','y'),candidate.sender))[kind]
            other='R' if chosen=='L' else 'L'
            equation(incentive_tex(i),caption=f'Type {kind}: stay with {chosen} versus switch to {other}',
                     tone='green' if i.passes else 'red')
            st.write(f'Follow type {kind}’s solid red signal, then the blue receiver action to its payoff. '+
                     f'The dashed red {other} branch is the hypothetical deviation. The two emphasised payoff pairs supply the numbers in the inequality.')
        else:
            equation(r'\boxed{\text{Pure-strategy PBE}}' if candidate.is_pbe else
                     r'\boxed{\text{Not a PBE}}',caption='Solver verdict',
                     tone='green' if candidate.is_pbe else 'red')
            st.write('Green reached paths mean this equilibrium has been explicitly confirmed.' if
                     st.session_state.get('revealed_profile')==(candidate.sender,candidate.receiver) else
                     'The red and blue paths show your manual profile. The solver checks receiver optimality, Bayes consistency and both sender incentives before confirming a PBE.')


def _path_derivation(game,candidate,focus):
    if focus['view_mode']!='Trace one path':
        return
    kind,signal,action=focus['kind'],focus['signal'],focus['action']
    prescribed=dict(zip(('x','y'),candidate.sender))[kind]
    selected_response=dict(zip(SIGNALS,candidate.receiver))[signal]
    incentive=next(i for i in candidate.incentives if i.kind==kind)
    with st.container(border=True,key='trace_derivation'):
        st.markdown(f'#### Traced calculation · type {kind}, signal {signal}')
        st.write(f'Player 2 sees {signal} but cannot see whether the sender is type x or y. '
                 f'The selected receiver response after {signal} is {selected_response} at both nodes.')
        p=candidate.posteriors[signal]
        equation(posterior_tex(game,candidate,signal) if p is not None else
                 interval_tex(candidate.beliefs[signal],signal),
                 caption=f'Belief after {signal}',tone='black')
        for possible in ACTIONS:
            equation(expected_tex(game,signal,possible,p),
                     caption=f'Player 2 payoff from {possible} after {signal}',tone='blue')
        st.write('The selected receiver action is supported by a valid belief.' if
                 candidate.beliefs[signal] is not None else
                 'The selected receiver action is not a best response for a valid belief.')
        equation(incentive_tex(incentive),
                 caption=f'Type {kind}: follow {prescribed} versus deviate to '+('R' if prescribed=='L' else 'L'),
                 tone='green' if incentive.passes else 'red')
        st.write('This sender incentive constraint holds.' if incentive.passes else
                 'This sender incentive constraint fails: switching signals is profitable.')
        st.write('The full candidate is a PBE for the displayed belief range.' if candidate.is_pbe else
                 'The full candidate is not a PBE. Both types and both receiver information sets must pass their checks.')


def _workings(game,candidate,focus):
    st.header('The Maths Behind the Game')
    st.caption('Every value below follows the selected strategy, responses, prior and payoff pairs.')
    with st.container(border=True,key='math_focus_controls'):
        st.radio('Focus a mathematical card',FOCUS_OPTIONS,key='math_focus')
        a,b,c=st.columns(3)
        a.selectbox('Signal to inspect',SIGNALS,key='focus_signal')
        b.selectbox('Action to evaluate',ACTIONS,key='focus_action')
        c.selectbox('Sender type to compare',('x','y'),key='focus_kind')
    st.markdown('#### 1 · Proposed strategy')
    st.write(f'Player 1: {sender_label(candidate.sender)}. Player 2: {receiver_label(candidate.receiver)}.')
    st.write('This is a separating candidate.' if candidate.separating else 'This is a pooling candidate.')
    st.markdown('#### 2 · Player 2’s beliefs')
    equation(r'\mu_s=P(x\mid s)',caption='Mu is the probability that Player 1 is type x after Player 2 observes signal s. The vertical bar means “given”.',tone='black')
    for signal in SIGNALS:
        belief_stages(game,candidate,signal)
    st.markdown('#### 3–4 · Expected utility and numerical substitution')
    st.write('Expected utility is Player 2’s payoff averaged across types using the belief after the observed signal.')
    for signal in SIGNALS:
        for action in ACTIONS:
            receiver_stages(game,signal,action,candidate.posteriors[signal])
    st.markdown('#### 5 · Receiver best responses')
    for signal,proposed in zip(SIGNALS,candidate.receiver):
        st.write(f'After {signal}, the selected response is {proposed}. Both possible responses are checked at the same information set.')
        for action in ACTIONS:
            equation(interval_tex(optimal_beliefs(game,signal,action),signal),
                     caption=f'Action {action} is optimal after {signal}',tone='blue')
        equation(interval_tex(candidate.beliefs[signal],signal),
                 caption=f'Beliefs that support selected action {proposed}, consistent with Bayes’ rule where applicable',tone='black')
    st.markdown('#### 6 · Sender incentive constraints')
    for incentive,signal in zip(candidate.incentives,candidate.sender):
        other='R' if signal=='L' else 'L'
        st.write(f'Type {incentive.kind}: stay with {signal}, or switch to {other}.')
        incentive_stages(incentive)
    st.write('Each type compares staying with switching signals while Player 2’s strategy remains fixed. Equality satisfies the constraint.')
    st.markdown('#### 7 · PBE conclusion')
    equation(r'\boxed{\text{Pure-strategy PBE}}' if candidate.is_pbe else
             r'\boxed{\text{Not a PBE}}',caption='Calculated verdict',tone='green' if candidate.is_pbe else 'red')
    st.write('Receiver optimality, Bayes consistency and both sender incentives hold for the displayed belief ranges.' if candidate.is_pbe else
             'At least one required condition fails. The red incentive checks or empty belief intervals above show why.')
    _render_criterion(game,candidate)


def _experiment(game):
    st.header('Experiment with the game')
    st.write('Change Nature’s prior or any of the eight terminal payoff pairs. The tree and all calculations update when you apply the edits.')
    equation(r'0<P(x)<1',caption='Both private types must remain possible',tone='black')
    if game != homework_game():
        st.info('The interactive tree and workings show your edited values. The Intuitive Criterion is only proved for the original game.')
    st.button('Reset to original homework',on_click=_reset)
    version=st.session_state.get('editor_version',0)
    with st.form(f'edit_game_{version}'):
        prior=st.number_input('Nature: probability of type x',min_value=.001,max_value=.999,
                              value=float(game.prior),step=.01,format='%.3f')
        rows=[{'Type':t,'Signal':s,'Action':a,'Player 1':float(game.payoff(t,s,a)),
               'Player 2':float(game.payoff(t,s,a,1))} for t,s,a in KEYS]
        edited=st.data_editor(rows,key=f'payoffs_{version}',hide_index=True,
                              disabled=['Type','Signal','Action'],num_rows='fixed',width='stretch',
                              column_config={p:st.column_config.NumberColumn(p,required=True) for p in ('Player 1','Player 2')})
        applied=st.form_submit_button('Apply changes',type='primary')
    if applied:
        try:
            new_game=Game(prior,{(r['Type'],r['Signal'],r['Action']):(r['Player 1'],r['Player 2']) for r in edited})
        except (ValueError,TypeError,ZeroDivisionError,OverflowError) as error:
            st.error(f'Please enter a finite number in every payoff cell. {error}')
        else:
            st.session_state.game=new_game
            st.session_state.editor_version=version+1
            _clear_verification()
            st.rerun()


def render_signalling_page():
    game=st.session_state.game
    st.header('Signalling Model · Seminar 3')
    st.markdown('''<div class="colour-legend" aria-label="Four pen colour legend">
<span><i style="background:#DC2626"></i>Red · Player 1 and deviations</span>
<span><i style="background:#2563EB"></i>Blue · Player 2</span>
<span><i style="background:#16803D"></i>Green · verified equilibrium</span>
<span><i style="background:#171717"></i>Black · beliefs and formulas</span></div>''',unsafe_allow_html=True)
    st.subheader('Choose a strategy')
    if st.session_state.get('tree_click_notice'):
        st.info(st.session_state.tree_click_notice)
    st.radio('Tree view',('Full strategy','Trace one path'),horizontal=True,key='tree_view_mode')
    if st.session_state.tree_view_mode=='Trace one path':
        st.button('Return to Full strategy',on_click=_full_strategy)
    with st.container(border=True,key='strategy_card'):
        sender=st.radio('Player 1 candidate strategy',SENDERS,
                        format_func=lambda s:('Separating' if s[0]!=s[1] else 'Pooling')+
                        f': x → {s[0]}, y → {s[1]}',key='tree_sender',
                        on_change=_clear_verification)
        a,b=st.columns(2)
        after_l=a.radio('Player 2 after L',ACTIONS,horizontal=True,key='tree_l',on_change=_clear_verification)
        after_r=b.radio('Player 2 after R',ACTIONS,horizontal=True,key='tree_r',on_change=_clear_verification)
        st.caption('One response after L applies to both L nodes; one response after R applies to both R nodes.')
        st.button('Show equilibrium ♡',on_click=_show_equilibrium,args=(game,))
    winners=[c for c in enumerate_candidates(game) if c.sender==sender and c.is_pbe]
    candidate=assess(game,sender,(after_l,after_r))
    confirmed=candidate.is_pbe and st.session_state.get('revealed_profile')==(sender,(after_l,after_r))
    status=('Verified PBE' if confirmed else
            'PBE conditions pass for some beliefs; press Show equilibrium to confirm' if candidate.is_pbe else
            'Not a PBE with these receiver actions')
    receiver_ok=all(candidate.beliefs[s] is not None for s in SIGNALS)
    sender_ok=all(i.passes for i in candidate.incentives)
    deviations={(i.kind,'R' if signal=='L' else 'L') for i,signal in zip(candidate.incentives,candidate.sender) if not i.passes}
    focus={'concept':st.session_state.math_focus,'signal':st.session_state.focus_signal,
           'action':st.session_state.focus_action,'kind':st.session_state.focus_kind,
           'view_mode':st.session_state.tree_view_mode,
           'compare_actions':st.session_state.focus_compare_actions}
    left,right=st.columns(2,gap='medium')
    for column,style,title,callback in (
        (left,'rectangular','Diagram A · compact signalling tree',_on_rect_tree_select),
        (right,'branching','Diagram B · branching game tree',_on_branch_tree_select),
    ):
        with column:
            with st.container(border=True,key=f'tree_card_{style}'):
                st.markdown(f'### {title}')
                figure=game_tree(game,sender,(after_l,after_r),confirmed=confirmed,
                                 deviations=deviations,focus=focus,compact=True,
                                 layout_style=style)
                chart_key=f"tree_chart_{style}_{st.session_state.get('tree_chart_version',0)}"
                st.session_state[f'tree_active_chart_key_{style}']=chart_key
                st.session_state[f'tree_target_names_{style}']=tuple(trace.name for trace in figure.data)
                st.plotly_chart(figure,width='stretch',key=chart_key,
                    on_select=callback,selection_mode='points',
                    config={'displayModeBar':False,'displaylogo':False})
                st.caption('Click L, R, u, d or a payoff. Dotted lines join each Player 2 information set.')
    st.write('**'+('Solver-confirmed equilibrium' if confirmed else 'Manual selection')+':** '+
             ('Separating' if candidate.separating else 'Pooling')+' · '+status)
    indicators=st.columns(3)
    indicators[0].metric('Receiver response','Supported' if receiver_ok else 'Fails')
    indicators[1].metric('Sender incentives','Pass' if sender_ok else 'Fail')
    indicators[2].metric('PBE status','PBE' if candidate.is_pbe else 'Not a PBE')
    if confirmed:
        st.success('Verified equilibrium paths are green in both trees.')
    for signal in SIGNALS:
        if candidate.beliefs[signal] is None:
            st.warning(f'Player 2 after {signal} is not optimal for a Bayes-consistent belief.')
    for kind,signal in zip(('x','y'),sender):
        action=(after_l if signal=='L' else after_r)
        pair=game.payoffs[kind,signal,action]
        st.write(f'Type {kind} → {signal} → {action}: payoff pair ({number(pair[0])}, {number(pair[1])})')
    _show_equilibrium_result(game,sender,winners)
    _focus_card(game,candidate,focus)
    with st.container(border=True,key='linked_math_panel'):
        st.markdown('#### Click an equation to trace it in both trees')
        cols=st.columns(2)
        for index,signal in enumerate(SIGNALS):
            cols[index].button(f'Belief after {signal}',key=f'math_belief_{signal}',
                               on_click=_select_math_focus,args=('Beliefs',signal))
        cols=st.columns(4)
        for index,(signal,action) in enumerate(((s,a) for s in SIGNALS for a in ACTIONS)):
            cols[index].button(f'Player 2: {action} after {signal}',key=f'math_eu_{signal}_{action}',
                               on_click=_select_math_focus,args=('Expected utility',signal,action))
        cols=st.columns(3)
        for index,kind in enumerate(('x','y')):
            cols[index].button(f'Type {kind} incentive inequality',key=f'math_ic_{kind}',
                               on_click=_select_math_focus,args=('Sender incentive constraints',None,None,kind))
        cols[2].button('PBE verification',key='math_pbe',
                       on_click=_select_math_focus,args=('Equilibrium conclusion',))
    _path_derivation(game,candidate,focus)
    _workings(game,candidate,focus)
    with st.expander('Compare all solver-supported pure-strategy PBE'):
        for c in winners:
            st.write(f'{sender_label(c.sender)} · {receiver_label(c.receiver)}')
            for signal in SIGNALS:
                equation(interval_tex(c.beliefs[signal],signal),caption=f'Belief after {signal}',tone='black')
    _experiment(game)
