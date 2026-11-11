"""One linked visual workspace for the six Seminar 2 moral-hazard questions."""
import streamlit as st
from moral_hazard_model import (Parameters, Contract, expected_utility, expected_profit,
    participation_slack, incentive_slack, feasible, scenario_result, trade_is_worthwhile)
from moral_hazard_visuals import decision_tree, contract_graph

TITLES={
  1:'Efficient effort',2:'Agent owns the firm',3:'Workers scarce · full information',
  4:'Firms scarce · full information',5:'Risk-neutral · hidden effort',
  6:'Risk-averse · hidden effort'}


def _initial():
    defaults={'mh_question':'Q1','mh_mode':'Explore','mh_p_high':.9,'mh_p_low':.7,
      'mh_output_high':100.0,'mh_output_low':0.0,'mh_cost':1.0,'mh_reservation':3.0,
      'mh_w1':4.5,'mh_w0':-.5,'mh_focus':'','mh_effort':'high',
      'mh_display':'proposed','mh_step':0,'mh_chart_version':0}
    for key,value in defaults.items():
        if key not in st.session_state: st.session_state[key]=value


def _reset():
    for key,value in {'mh_p_high':.9,'mh_p_low':.7,'mh_output_high':100.0,
      'mh_output_low':0.0,'mh_cost':1.0,'mh_reservation':3.0,
      'mh_w1':4.5,'mh_w0':-.5,'mh_focus':'','mh_effort':'high',
      'mh_display':'proposed','mh_step':0}.items():
        st.session_state[key]=value
    st.session_state.mh_chart_version+=1


def _wage_changed():
    st.session_state.mh_display='proposed'


def _question_changed():
    st.session_state.mh_step=0
    st.session_state.mh_focus=''
    st.session_state.mh_display='proposed'
    st.session_state.mh_chart_version+=1


def _focus(target):
    st.session_state.mh_focus=target
    if target in ('effort_high','effort_low'):
        st.session_state.mh_effort=target.split('_')[1]
    st.session_state.mh_chart_version+=1


def _pick_event(key,names):
    event=st.session_state.get(key)
    if not event: return
    for point in event.get('selection',{}).get('points',[]):
        i=point.get('curve_number',point.get('curveNumber'))
        if isinstance(i,int) and 0<=i<len(names):
            target=names[i]
            if target in ('IR','IC','Isoprofit','optimal','optimal_low','proposed'):
                _focus({'IR':'ir','IC':'ic','Isoprofit':'profit',
                        'optimal':'optimal','optimal_low':'optimal','proposed':'wage'}[target]); return
            if target.startswith(('effort_','outcome_')):
                _focus(target); return


def _tree_select():
    key=st.session_state.get('mh_tree_key')
    _pick_event(key,st.session_state.get('mh_tree_names',()))


def _graph_select():
    key=st.session_state.get('mh_graph_key')
    _pick_event(key,st.session_state.get('mh_graph_names',()))


def _fmt(n):
    return f'{n:.3f}'.rstrip('0').rstrip('.') if abs(n)<10000 else f'{n:.1f}'


def _parameter_panel():
    with st.expander('Change the Seminar 2 parameters',expanded=False):
        a,b,c=st.columns(3)
        a.number_input('P(high output | high effort)',min_value=0.0,max_value=1.0,step=.05,key='mh_p_high')
        b.number_input('P(high output | low effort)',min_value=0.0,max_value=1.0,step=.05,key='mh_p_low')
        c.number_input('High-effort cost',min_value=0.0,step=.25,key='mh_cost')
        a.number_input('High output',min_value=0.0,step=5.0,key='mh_output_high')
        b.number_input('Low output',min_value=0.0,step=5.0,key='mh_output_low')
        c.number_input('Reservation utility',min_value=0.0,step=.25,key='mh_reservation')
        st.button('Reset to Seminar 2 values',on_click=_reset)


def _guided_math(params,q,displayed,optimum,high,low,stage):
    """Reveal only the current derivation step, keeping later answers hidden."""
    index,concept=stage
    p=params.probability(displayed.effort)
    if concept=='profit' and index==0:
        st.latex(r'\max_{w_0,w_1}\ E[\pi_P]=p_e(q_1-w_1)+(1-p_e)(q_0-w_0)')
        st.write('The principal values output and pays the wage promised for each outcome.')
    elif concept=='ir':
        st.latex(r'\mathrm{IR}:\quad p_e u(w_1)+(1-p_e)u(w_0)-c(e)\ge\bar U')
        st.write('The agent accepts only if expected utility reaches the outside option.')
    elif concept=='ic':
        fn=r'\sqrt{w}' if q!=5 else 'w'
        st.latex(rf'\mathrm{{IC}}:\quad ({_fmt(params.gap)})'
                 rf'({fn.replace("w","w_1")}-{fn.replace("w","w_0")})\ge {_fmt(params.effort_cost)}')
        st.write('Compare the prescribed effort with the hidden deviation under the same output-based wages.')
    elif concept=='wage' and q==6 and index==3:
        st.latex(r'w_0\ge0,\qquad w_1\ge0')
        st.write('Square-root utility cannot evaluate a negative wage. Check this domain before solving the constraints.')
    elif concept=='wage':
        st.latex(rf'w_0^*={_fmt(high.w0)},\qquad w_1^*={_fmt(high.w1)}')
        st.write('These wages minimise expected payment among feasible high-effort contracts; compare them with low effort next.')
    elif concept=='optimal':
        if q in (2,3):
            a=expected_utility(params,high,'high'); b=expected_utility(params,low,'low')
            st.latex(rf'E[U_A\mid H]={_fmt(a)},\qquad E[U_A\mid L]={_fmt(b)}')
        else:
            a=expected_profit(params,high,'high'); b=expected_profit(params,low,'low')
            st.latex(rf'\pi_H^*={_fmt(a)},\qquad \pi_L^*={_fmt(b)}')
        st.success(f'The compared solution chooses {optimum.effort} effort.')
    else:
        st.latex(rf'E[U_A\mid H]={_fmt(expected_utility(params,high,"high"))},\qquad '
                 rf'E[U_A\mid L]={_fmt(expected_utility(params,low,"low"))}')
        st.write('Compare expected utilities using the outcome probabilities for each effort.')


def _maths(params,q,proposed,displayed,optimum,high,low,trade,guide_stage=None):
    e=displayed.effort; p=params.probability(e); c=params.cost(e)
    kind=displayed.utility_kind
    fn=r'\sqrt{w}' if kind=='sqrt' else 'w'
    st.markdown('### The mathematics behind the decision')
    st.caption(('The blue contract is your proposal; the green point is the computed optimum. '
                'A selected contract is not automatically feasible or optimal.') if q>=5 else
               'Effort can be observed in this question. Wages may be conditioned on verifiable effort.')
    if guide_stage is not None:
        _guided_math(params,q,displayed,optimum,high,low,guide_stage)
        return
    cols=st.columns(4)
    for col,label,target in ((cols[0],'Expected utility','ir'),(cols[1],'Incentive comparison','ic'),
                              (cols[2],'Expected profit','profit'),(cols[3],'Optimal contract','optimal')):
        col.button(label,use_container_width=True,on_click=_focus,args=(target,),
                   type='primary' if st.session_state.mh_focus==target else 'secondary')
    if st.session_state.mh_focus.startswith('outcome_'):
        _,effort,outcome=st.session_state.mh_focus.split('_')
        st.info(f'Tracing {effort} effort and {outcome} output in the tree. The terminal displays output, wage, agent utility and principal profit.')
    st.latex(rf'E[U_A\mid {e[0].upper()}]={_fmt(p)}{fn.replace("w", "w_1")}+'
             rf'{_fmt(1-p)}{fn.replace("w", "w_0")}-{_fmt(c)}')
    st.latex(rf'E[U_A\mid {e[0].upper()}]={_fmt(expected_utility(params,displayed,e))},\qquad '
             rf'\bar U={_fmt(params.reservation)}')
    if q>=5:
        other='low' if e=='high' else 'high'
        ir_slack=participation_slack(params,displayed)
        ic_slack=incentive_slack(params,displayed)
        st.latex(rf'\mathrm{{IR}}:\quad E[U_A\mid {e[0].upper()}]-\bar U='
                 rf'{_fmt(ir_slack)}{"<" if ir_slack < -1e-8 else r"\ge"} 0')
        st.latex(rf'\mathrm{{IC}}:\quad E[U_A\mid {e[0].upper()}]-E[U_A\mid {other[0].upper()}]='
                 rf'{_fmt(ic_slack)}{"<" if ic_slack < -1e-8 else r"\ge"} 0')
        if e=='high':
            u1=fn.replace('w','w_1');u0=fn.replace('w','w_0')
            st.latex(rf'({_fmt(params.gap)})({u1}-{u0})\ge {_fmt(params.effort_cost)}')
        else:
            u1=fn.replace('w','w_1');u0=fn.replace('w','w_0')
            st.latex(rf'({_fmt(params.gap)})({u1}-{u0})\le {_fmt(params.effort_cost)}')
        ir=participation_slack(params,displayed); ic=incentive_slack(params,displayed)
        valid=feasible(params,displayed,hidden=True)
        status=lambda slack:'binding' if abs(slack)<1e-8 else 'satisfied' if slack>0 else 'violated'
        st.write(f'**Your contract:** IR {status(ir)}; IC {status(ic)}. '+
                 ('Feasible for the prescribed effort.' if valid else 'Not feasible for the prescribed effort.'))
        if abs(ic)<1e-8:
            st.caption('IC equality makes the agent indifferent. Inducing the prescribed effort requires tie-breaking in its favour.')
    else:
        st.info('Effort is observable and enforceable here, so the hidden-action IC constraint is not imposed on the on-path wage schedule.')
    st.latex(rf'E[\pi_P\mid {e[0].upper()}]={_fmt(p)}({_fmt(params.output_high)}-w_1)+'
             rf'{_fmt(1-p)}({_fmt(params.output_low)}-w_0)='
             rf'{_fmt(expected_profit(params,displayed,e))}')
    if q==1:
        st.latex(rf'V_H={_fmt(expected_profit(params,high,"high"))},\qquad V_L={_fmt(expected_profit(params,low,"low"))}')
        st.caption('V is expected output minus the least costly insured wage meeting the reservation utility; it measures value above that participation requirement.')
    elif q==2:
        st.latex(rf'E[U_A\mid H]={_fmt(expected_utility(params,high,"high"))},\qquad '
                 rf'E[U_A\mid L]={_fmt(expected_utility(params,low,"low"))}')
    elif q==3:
        st.latex(rf'\pi_P=0,\qquad w_H=E[Q\mid H]={_fmt(high.w1)},\quad '
                 rf'w_L=E[Q\mid L]={_fmt(low.w1)}')
    elif q==4:
        st.latex(rf'w_H=(\bar U+c)^2={_fmt(high.w1)},\qquad w_L=\bar U^2={_fmt(low.w1)}')
    elif q==5:
        relation=r'\ge' if e=='high' else r'\le'
        st.latex(rf'w_1-w_0{relation}\frac{{c}}{{p_H-p_L}}={_fmt(params.effort_cost/params.gap)}')
        st.write('With linear utility and no limited liability, every high-effort contract on the IR line satisfying IC has the same optimal high-effort profit. The green point is one representative, not the only optimum.')
    else:
        relation=r'\ge' if e=='high' else r'\le'
        st.latex(rf'\sqrt{{w_1}}-\sqrt{{w_0}}{relation} '
                 rf'\frac{{c}}{{p_H-p_L}}={_fmt(params.effort_cost/params.gap)}')
        if participation_slack(params,high)>1e-8:
            st.write('At the high-effort cost minimum, the low-output wage reaches zero and IR is slack. The generic lecture result that both IR and IC bind assumes utility can take negative values; square-root utility cannot.')
        else:
            st.write('At the high-effort cost minimum, both IR and IC bind. This result respects the nonnegative wage domain.')
    choice=('H' if optimum.effort=='high' else 'L') if trade else r'\varnothing'
    st.latex(rf'\pi_H^*={_fmt(expected_profit(params,high,"high"))},\qquad '
             rf'\pi_L^*={_fmt(expected_profit(params,low,"low"))},\qquad '
             rf'e^*={choice}')
    if not trade:
        st.warning('The best conditional contract does not beat the outside option. No trade is the global choice under these parameters.')


def _guide(q):
    steps={
      1:[('Compare output','profit'),('Insure each effort at minimum cost','ir'),('Compare surplus','optimal')],
      2:[('Give the agent residual output','wage'),('Compare expected utility by effort','ic'),('Choose effort','optimal')],
      3:[('Let the worker capture expected output','wage'),('Compare utilities','profit'),('Choose the worker-preferred effort','optimal')],
      4:[('Write the participation condition','ir'),('Use full insurance','wage'),('Compare principal profit','profit'),('Choose effort','optimal')],
      5:[('Write expected profit','profit'),('Write IR','ir'),('Write IC','ic'),('Find the optimal wage ray','wage'),('Compare high and low effort','optimal')],
      6:[('Write expected profit','profit'),('Write IR','ir'),('Write IC','ic'),('Respect w₀,w₁ ≥ 0','wage'),('Minimise wage cost','wage'),('Compare high and low effort','optimal')]}
    sequence=steps[q]
    if st.session_state.mh_step>=len(sequence): st.session_state.mh_step=0
    st.markdown(f'**Step {st.session_state.mh_step+1} of {len(sequence)} · {sequence[st.session_state.mh_step][0]}**')
    if st.button('Reveal next step →'):
        st.session_state.mh_step=min(st.session_state.mh_step+1,len(sequence)-1)
        st.session_state.mh_focus=sequence[st.session_state.mh_step][1]
        st.rerun()
    return st.session_state.mh_step,sequence[st.session_state.mh_step][1]


def render_moral_hazard_page():
    _initial()
    st.header('Moral Hazard · Seminar 2')
    st.radio('Choose a question',tuple(f'Q{i}' for i in range(1,7)),horizontal=True,
             key='mh_question',on_change=_question_changed)
    q=int(st.session_state.mh_question[1:])
    show_optimal=(st.session_state.mh_mode=='Explore' or
                  st.session_state.mh_display=='optimal' or
                  st.session_state.mh_step>={1:2,2:2,3:2,4:3,5:4,6:5}[q])
    st.subheader(f'Q{q} · {TITLES[q]}')
    st.radio('Learning mode',('Explore','Solve with me'),horizontal=True,key='mh_mode')
    st.caption('Red · agent effort and IC     Blue · wages and IR     Green · verified optimum     Black · probabilities and neutral labels')
    _parameter_panel()
    try:
        params=Parameters(st.session_state.mh_p_high,st.session_state.mh_p_low,
                          st.session_state.mh_output_high,st.session_state.mh_output_low,
                          st.session_state.mh_cost,st.session_state.mh_reservation)
    except ValueError as exc:
        st.error(str(exc)); st.stop()
    kind='linear' if q==5 else 'sqrt'
    a,b,c,d=st.columns([1,1,1,1])
    min_w=None if kind=='linear' else 0.0
    if kind=='sqrt' and st.session_state.mh_w0<0: st.session_state.mh_w0=0.0
    if kind=='sqrt' and st.session_state.mh_w1<0: st.session_state.mh_w1=0.0
    a.number_input('Low-output wage w₀',min_value=min_w,step=.5,key='mh_w0',
                   on_change=_wage_changed,disabled=q==2)
    b.number_input('High-output wage w₁',min_value=min_w,step=.5,key='mh_w1',
                   on_change=_wage_changed,disabled=q==2)
    c.selectbox('Prescribed effort',('high','low'),key='mh_effort')
    if d.button('Show optimal contract',use_container_width=True):
        st.session_state.mh_display='optimal';st.session_state.mh_focus='optimal';st.session_state.mh_chart_version+=1
    compare_a,compare_b=st.columns(2)
    if compare_a.button('Compare high and low effort',use_container_width=True):
        st.session_state.mh_focus='profit';st.session_state.mh_chart_version+=1
    if compare_b.button('Compare prescribed effort with deviation',use_container_width=True):
        st.session_state.mh_focus='ic';st.session_state.mh_chart_version+=1
    optimum,high,low=scenario_result(params,q)
    trade=trade_is_worthwhile(params,q,high,low)
    proposed=Contract(st.session_state.mh_w0,st.session_state.mh_w1,
                      st.session_state.mh_effort,kind,'Your proposed contract')
    displayed=optimum if q==2 or st.session_state.mh_display=='optimal' else proposed
    if q==2: st.caption('The agent owns the firm and receives output directly, so there is no wage contract to edit in Q2.')
    if q in (1,2,3,4):
        # Effort is contractible; each branch can have an effort-contingent offer.
        contracts={'high':high,'low':low}
        contracts[displayed.effort]=displayed
    else:
        # Hidden effort: the same output-contingent wages apply after either action.
        contracts={'high':displayed,'low':displayed}
    with st.container(key='mh_visual_grid'):
        left,right=st.columns(2,gap='medium')
        with left:
            with st.container(border=True):
                st.markdown('#### Principal–agent decision tree')
                tree=decision_tree(params,contracts,displayed.effort,st.session_state.mh_focus,
                                   hidden=q>=5)
                key=f'mh_tree_{st.session_state.mh_chart_version}'
                st.session_state.mh_tree_key=key
                st.session_state.mh_tree_names=tuple(t.name for t in tree.data)
                st.plotly_chart(tree,width='stretch',key=key,on_select=_tree_select,
                                selection_mode='points',config={'displayModeBar':False})
                st.caption('Click an effort or outcome to trace it through the maths.')
        with right:
            with st.container(border=True):
                st.markdown('#### Contract and payoff graph')
                graph=contract_graph(params,q,proposed,optimum,high,low,
                                     st.session_state.mh_focus,trade,show_optimal,
                                     displayed.effort)
                key=f'mh_graph_{st.session_state.mh_chart_version}'
                st.session_state.mh_graph_key=key
                st.session_state.mh_graph_names=tuple(t.name for t in graph.data)
                st.plotly_chart(graph,width='stretch',key=key,on_select=_graph_select,
                                selection_mode='points',config={'displayModeBar':False})
                st.caption('Click IR, IC, an effort point or a contract to focus its derivation.')
    guide_stage=_guide(q) if st.session_state.mh_mode=='Solve with me' else None
    _maths(params,q,proposed,displayed,optimum,high,low,trade,guide_stage)
    with st.container(border=True):
        st.markdown('#### Economic intuition')
        if guide_stage is not None and guide_stage[1]!='optimal':
            st.write('Use the current highlighted equation to decide which condition to check next.')
        elif q==1: st.write('High effort raises expected output enough to cover the extra insured wage needed to compensate effort.')
        elif q==2: st.write('The owner receives the output directly, so effort raises the chance of a high personal income. Ownership exposes this risk-averse agent to output risk.')
        elif q==3: st.write('Competing firms leave profit at zero. The worker captures the surplus and prefers a certain wage to a risky wage with the same mean.')
        elif q==4: st.write('When firms have bargaining power, the cheapest full-information contract pays a constant wage that just meets participation. The principal compares profits across enforceable efforts.')
        elif q==5: st.write('Without limited liability, a negative low-output wage can fund stronger incentives. The risk-neutral agent does not require a risk premium, and many contracts on the optimal ray tie.')
        else: st.write('With square-root utility, negative wages are impossible. The principal balances incentives against insurance and compares the best high-effort contract with a low-effort insured contract.')
