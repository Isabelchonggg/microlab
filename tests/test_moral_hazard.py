"""Seminar 2 values, domain checks, and the two linked visual panels."""
import json
from math import isclose
import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from moral_hazard_model import (Parameters, Contract, expected_utility, expected_profit,
    participation_slack, incentive_slack, feasible, scenario_result, trade_is_worthwhile)
from moral_hazard_page import _pick_event
from moral_hazard_visuals import contract_graph, decision_tree

APP=str(Path(__file__).resolve().parents[1]/'app.py')


def test_six_original_scenarios():
    p=Parameters()
    assert p.output('high')==90 and p.output('low')==70
    winners={1:'high',2:'high',3:'high',4:'high',5:'high',6:'high'}
    for q in range(1,7):
        winner,high,low=scenario_result(p,q)
        assert winner.effort==winners[q]
        assert min(high.w0,high.w1)>=0 or q==5
    _,h,l=scenario_result(p,4)
    assert (h.w0,h.w1,l.w0,l.w1)==(16,16,9,9)
    _,h,l=scenario_result(p,5)
    assert (h.w0,h.w1)==pytest.approx((-.5,4.5))
    assert expected_profit(p,h,'high')==pytest.approx(86)
    assert expected_profit(p,l,'low')==pytest.approx(67)
    assert participation_slack(p,h)==pytest.approx(0)
    assert incentive_slack(p,h)==pytest.approx(0)
    _,h,l=scenario_result(p,6)
    assert (h.w0,h.w1)==pytest.approx((0,25))
    assert expected_profit(p,h,'high')==pytest.approx(67.5)
    assert expected_profit(p,l,'low')==pytest.approx(61)
    assert participation_slack(p,h)==pytest.approx(.5)
    assert incentive_slack(p,h)==pytest.approx(0)


def test_domains_and_feasibility():
    with pytest.raises(ValueError): Parameters(p_high=.6,p_low=.7)
    with pytest.raises(ValueError): Parameters(output_low=-1)
    p=Parameters()
    bad=Contract(-.5,4.5,'high','sqrt')
    assert not feasible(p,bad)
    with pytest.raises(ValueError): expected_utility(p,bad,'high')
    linear=Contract(-.5,4.5,'high','linear')
    assert feasible(p,linear)
    assert not feasible(p,linear,limited_liability=True)
    assert not feasible(p,Contract(0,4.5,'high','linear'))
    assert scenario_result(Parameters(p_high=1),6)[1].w0==0
    no_trade=Parameters(output_high=1,output_low=0)
    _,high,low=scenario_result(no_trade,6)
    assert not trade_is_worthwhile(no_trade,6,high,low)


def test_visuals_derive_from_shared_state():
    p=Parameters(); optimum,high,low=scenario_result(p,6)
    proposed=Contract(0,16,'high','sqrt')
    tree=decision_tree(p,{'high':proposed,'low':proposed},'high',hidden=True)
    names={t.name for t in tree.data}
    assert {'effort_high','effort_low','outcome_high_high','outcome_low_low'}<=names
    assert any('w=16.00' in str(t.text[0]) for t in tree.data if t.name=='outcome_high_high')
    chart=contract_graph(p,6,proposed,optimum,high,low)
    traces={t.name:t for t in chart.data}
    assert {'IR','IC','optimal','proposed'}<=set(traces)
    assert traces['optimal'].x[0]==0
    assert traces['optimal'].y[0]==pytest.approx(25)
    low_graph=contract_graph(p,6,Contract(0,16,'low','sqrt'),optimum,high,low,
                             selected_effort='low')
    low_traces={t.name:t for t in low_graph.data}
    assert 'Low-effort feasible region' in low_traces
    assert low_traces['IR'].y[0]==pytest.approx((3/.7)**2)


def test_app_all_questions_and_interaction_state():
    app=AppTest.from_file(APP,default_timeout=20).run()
    app.radio[0].set_value('Moral Hazard Model').run()
    assert not app.exception
    for q in range(1,7):
        app.radio(key='mh_question').set_value(f'Q{q}').run()
        assert not app.exception and len(app.get('plotly_chart'))==2
        assert app.session_state.mh_question==f'Q{q}'
    app.number_input(key='mh_w1').set_value(25).run()
    assert not app.exception
    assert app.session_state.mh_display=='proposed'
    specs=[json.loads(c.proto.spec) for c in app.get('plotly_chart')]
    assert any('w=25.00' in str(t.get('text')) for t in specs[0]['data'])
    assert any(t.get('name')=='proposed' and t['y']==[25] for t in specs[1]['data'])
    app.selectbox(key='mh_effort').set_value('low').run()
    low_spec=json.loads(app.get('plotly_chart')[1].proto.spec)
    assert any(t.get('name')=='Low-effort feasible region' for t in low_spec['data'])
    assert any(r'\le' in eq.value for eq in app.latex)
    next(b for b in app.button if b.label=='Show optimal contract').click().run()
    assert not app.exception and app.session_state.mh_display=='optimal'
    app.radio(key='mh_question').set_value('Q5').run()
    assert not app.exception
    app.radio[0].set_value('Signalling Model').run()
    assert not app.exception and len(app.get('plotly_chart'))==2


def test_guided_mode_reveals_one_step_and_hides_optimum():
    app=AppTest.from_file(APP,default_timeout=20).run()
    app.radio[0].set_value('Moral Hazard Model').run()
    app.radio(key='mh_question').set_value('Q6').run()
    app.radio(key='mh_mode').set_value('Solve with me').run()
    assert not app.exception
    graph=json.loads(app.get('plotly_chart')[1].proto.spec)
    assert not any(t.get('name')=='optimal' for t in graph['data'])
    assert not any(r'\pi_H^*' in eq.value for eq in app.latex)
    for _ in range(5):
        next(b for b in app.button if b.label=='Reveal next step →').click().run()
        assert not app.exception
    graph=json.loads(app.get('plotly_chart')[1].proto.spec)
    assert any(t.get('name')=='optimal' for t in graph['data'])
