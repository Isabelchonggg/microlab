"""Streamlit transitions share one selection across tree, maths and controls."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from solver import assess
from signalling_page import _apply_tree_click, _selected_tree_target

APP=str(Path(__file__).resolve().parents[1]/'app.py')
SENDERS=(('L','R'),('R','L'),('L','L'),('R','R'))
RED,BLUE,GREEN='#DC2626','#2563EB','#16803D'


def open_app():
    app=AppTest.from_file(APP,default_timeout=20).run()
    assert not app.exception
    return app


def click(app,label):
    next(b for b in app.button if b.label==label).click().run()
    assert not app.exception


def figure(app):
    return json.loads(app.get('plotly_chart')[0].proto.spec)


def second_tree(app):
    return json.loads(app.get('plotly_chart')[1].proto.spec)


def test_both_diagrams_stay_visible_in_both_modes_and_share_focus():
    app=open_app()
    assert len(app.get('plotly_chart'))==2
    for tree in (figure(app),second_tree(app)):
        assert sum((t.get('name') or '').startswith('select:terminal:') for t in tree['data'])==8
    assert figure(app)['layout']['shapes'][0]['x0']==figure(app)['layout']['shapes'][0]['x1']
    assert second_tree(app)['layout']['shapes'][0]['y0']==second_tree(app)['layout']['shapes'][0]['y1']
    app.radio(key='tree_view_mode').set_value('Trace one path').run()
    assert len(app.get('plotly_chart'))==2
    click(app,'Belief after R')
    assert len(app.get('plotly_chart'))==2
    assert figure(app)['layout']['shapes'][1]['line']['width']==4
    assert second_tree(app)['layout']['shapes'][1]['line']['width']==4
    click(app,'Return to Full strategy')
    assert len(app.get('plotly_chart'))==2


def branches(app):
    return {t['name']:t for t in figure(app)['data'] if 'line' in t and t.get('name')}


def test_tree_click_targets_update_shared_controls_and_reset_verification():
    app=open_app()
    names=[trace.get('name') for trace in figure(app)['data']]
    for target in ('select:sender:x:R','select:sender:y:L',
                   'select:receiver:x:L:d','select:receiver:y:R:d',
                   'select:terminal:x:R:u'):
        assert target in names
        index=names.index(target)
        event={'selection':{'points':[{'curve_number':index}]}}
        assert _selected_tree_target(event,names)==target
    state={'tree_sender':('L','R'),'tree_l':'u','tree_r':'u',
           'revealed_profile':(('L','R'),('u','d'))}
    assert _apply_tree_click('select:sender:x:R',state)
    assert state['tree_sender']==('R','R')
    assert 'revealed_profile' not in state
    assert _apply_tree_click('select:sender:y:L',state)
    assert state['tree_sender']==('R','L')
    assert _apply_tree_click('select:receiver:x:L:d',state)
    assert (state['tree_l'],state['tree_r'])==('d','u')
    assert _apply_tree_click('select:receiver:y:R:d',state)
    assert (state['tree_l'],state['tree_r'])==('d','d')
    assert state['tree_chart_version']==4
    assert not _apply_tree_click('select:receiver:y:R:d',state)
    assert _apply_tree_click('select:terminal:x:L:u',state)
    assert state['tree_sender']==('L','L')
    assert (state['tree_l'],state['tree_r'])==('u','d')
    assert state['tree_view_mode']=='Trace one path'
    assert state['focus_kind']=='x' and state['focus_signal']=='L'


def test_clickable_equation_buttons_update_tree_focus():
    app=open_app()
    click(app,'Belief after R')
    assert app.session_state['math_focus']=='Beliefs'
    assert app.session_state['focus_signal']=='R'
    assert app.session_state['tree_view_mode']=='Trace one path'
    assert figure(app)['layout']['shapes'][1]['line']['width']==4
    assert any('Traced calculation' in m.value for m in app.markdown)
    assert any(r'E[U_2(u\mid R)]' in e.value for e in app.latex)
    assert any(r'E[U_2(d\mid R)]' in e.value for e in app.latex)
    click(app,'Player 2: d after L')
    assert app.session_state['math_focus']=='Expected utility'
    assert app.session_state['focus_signal']=='L'
    assert app.session_state['focus_action']=='d'
    assert branches(app)['x/L → d']['line']['width']==6
    click(app,'Type y incentive inequality')
    assert app.session_state['focus_kind']=='y'
    assert branches(app)['y → L']['line']['dash']=='dash'
    click(app,'Return to Full strategy')
    assert app.session_state['tree_view_mode']=='Full strategy'
    assert app.session_state['math_focus']=='Overview'


def test_all_receiver_profiles_and_terminal_click_trace_model_payoffs():
    app=open_app()
    for left in ('u','d'):
        for right in ('u','d'):
            app.radio(key='tree_l').set_value(left).run()
            app.radio(key='tree_r').set_value(right).run()
            assert not app.exception
            for tree in (figure(app),second_tree(app)):
                lines={t['name']:t for t in tree['data'] if 'line' in t and t.get('name')}
                assert all(lines[f'{kind}/L → {left}']['line']['color']==BLUE for kind in ('x','y'))
                assert all(lines[f'{kind}/R → {right}']['line']['color']==BLUE for kind in ('x','y'))
            candidate=assess(app.session_state['game'],app.session_state['tree_sender'],(left,right))
            assert ('PBE' if candidate.is_pbe else 'Not a PBE') in [m.value for m in app.metric if m.label=='PBE status'][0]
    state={'tree_sender':('L','R'),'tree_l':'u','tree_r':'d'}
    assert _apply_tree_click('select:terminal:y:L:d',state)
    assert state['tree_sender']==('L','L')
    assert state['tree_l']=='d' and state['tree_r']=='d'
    assert (state['focus_kind'],state['focus_signal'],state['focus_action'])==('y','L','d')
    game=app.session_state['game']
    assert game.payoffs['y','L','d']==(0,1)


def test_single_page_four_candidates_and_no_original_image():
    app=open_app()
    assert not app.tabs
    assert app.radio(key='tree_sender').options==[
        'Separating: x → L, y → R','Separating: x → R, y → L',
        'Pooling: x → L, y → L','Pooling: x → R, y → R']
    assert any(h.value=='The Maths Behind the Game' for h in app.header)
    assert any(h.value=='Experiment with the game' for h in app.header)
    assert not any('Original seminar question' in m.value for m in app.markdown)
    assert app.radio(key='math_focus').value=='Overview'
    assert len(app.latex)>20


def test_all_four_strategy_transitions_update_tree_and_maths_back_and_forth():
    app=open_app()
    for sender in (*SENDERS, SENDERS[0], SENDERS[3]):
        app.radio(key='tree_sender').set_value(sender).run()
        assert not app.exception
        for tree in (figure(app),second_tree(app)):
            lines={t['name']:t for t in tree['data'] if 'line' in t and t.get('name')}
            for kind,signal in zip(('x','y'),sender):
                assert lines[f'{kind} → {signal}']['line']['color']==RED
                other='R' if signal=='L' else 'L'
                if lines[f'{kind} → {other}']['line']['color']==RED:
                    assert lines[f'{kind} → {other}']['line']['dash']=='dash'
        candidate=assess(app.session_state['game'],sender,
                         (app.session_state['tree_l'],app.session_state['tree_r']))
        assert candidate.separating==(sender[0]!=sender[1])
        classification='separating candidate' if candidate.separating else 'pooling candidate'
        assert any(classification in m.value for m in app.markdown)
        for signal,posterior in candidate.posteriors.items():
            if posterior is not None:
                assert any(f'\\mu_{{{signal}}}' in e.value for e in app.latex)


def test_receiver_controls_independent_and_shared_by_information_set():
    app=open_app()
    app.radio(key='tree_l').set_value('d').run()
    assert (app.session_state['tree_l'],app.session_state['tree_r'])==('d','u')
    lines=branches(app)
    assert lines['x/L → d']['line']['color']==lines['y/L → d']['line']['color']==BLUE
    assert lines['x/R → u']['line']['color']==lines['y/R → u']['line']['color']==BLUE
    assert all(lines[f'{kind}/L → d']['line']['dash']=='solid' for kind in ('x','y'))
    app.radio(key='tree_r').set_value('d').run()
    assert (app.session_state['tree_l'],app.session_state['tree_r'])==('d','d')
    lines=branches(app)
    assert lines['x/R → d']['line']['color']==lines['y/R → d']['line']['color']==BLUE
    assert 'revealed_profile' not in app.session_state
    assert any('not optimal' in w.value for w in app.warning)


def test_math_cards_focus_exact_branches_and_payoffs():
    app=open_app()
    app.radio(key='math_focus').set_value('Beliefs').run()
    app.selectbox(key='focus_signal').set_value('R').run()
    assert app.session_state['math_focus']=='Beliefs'
    assert app.session_state['focus_signal']=='R'
    assert figure(app)['layout']['shapes'][1]['line']['width']==4
    assert branches(app)['y → R']['opacity']==1
    assert branches(app)['x → L']['opacity']<1
    assert any('Belief after R' in c.value for c in app.caption)
    app.radio(key='math_focus').set_value('Expected utility').run()
    app.selectbox(key='focus_action').set_value('d').run()
    assert branches(app)['x/R → d']['line']['width']==6
    assert branches(app)['y/R → d']['line']['width']==6
    assert any(r'E[U_2(d\mid R)]' in e.value for e in app.latex)
    app.radio(key='math_focus').set_value('Receiver best responses').run()
    assert figure(app)['layout']['shapes'][1]['line']['width']==4
    assert any('After R' in m.value or 'after R' in m.value for m in app.markdown)
    app.radio(key='math_focus').set_value('Sender incentive constraints').run()
    app.selectbox(key='focus_kind').set_value('y').run()
    lines=branches(app)
    assert lines['y → L']['line']['dash']=='dash'
    assert lines['y → L']['line']['color']==RED
    assert lines['y/R → u']['line']['width']==6
    assert lines['y/L → u']['line']['width']==6
    assert any('Type y: stay with R versus switch to L' in c.value for c in app.caption)
    app.radio(key='math_focus').set_value('Equilibrium conclusion').run()
    assert any('Solver verdict' in c.value for c in app.caption)
    app.radio(key='math_focus').set_value('Beliefs').run()
    assert figure(app)['layout']['shapes'][1]['line']['width']==4


def test_show_equilibrium_unique_and_pooling_alternatives():
    app=open_app()
    click(app,'Show equilibrium ♡')
    assert app.session_state['revealed_profile']==(('L','R'),('u','d'))
    assert branches(app)['x → L']['line']['color']==GREEN
    app.radio(key='tree_sender').set_value(('R','R')).run()
    before=(app.session_state['tree_l'],app.session_state['tree_r'])
    click(app,'Show equilibrium ♡')
    assert (app.session_state['tree_l'],app.session_state['tree_r'])==before
    assert any('2 receiver profiles' in s.value for s in app.success)
    assert any(b.label=='Use equilibrium option 2' for b in app.button)
    assert any(r'\frac{1}{2}\le \mu_{L}\le 1' in e.value for e in app.latex)
    assert any(r'0\le \mu_{L}\le \frac{1}{2}' in e.value for e in app.latex)
    click(app,'Use equilibrium option 2')
    assert app.session_state['revealed_profile']==(('R','R'),('d','u'))
    assert branches(app)['y → R']['line']['color']==GREEN


def test_no_pbe_candidates_keep_manual_receiver_choices():
    app=open_app()
    for sender in (('R','L'),('L','L')):
        app.radio(key='tree_sender').set_value(sender).run()
        before=(app.session_state['tree_l'],app.session_state['tree_r'])
        click(app,'Show equilibrium ♡')
        assert any('No pure-strategy PBE' in w.value for w in app.warning)
        assert (app.session_state['tree_l'],app.session_state['tree_r'])==before
        assert 'revealed_profile' not in app.session_state


def test_prior_and_payoff_edits_recalculate_then_reset():
    app=open_app()
    app.number_input[0].set_value(.25)
    click(app,'Apply changes')
    assert float(app.session_state['game'].prior)==.25
    assert any('only proved for the original game' in i.value for i in app.info)
    click(app,'Reset to original homework')
    assert float(app.session_state['game'].prior)==.5
    app.session_state[f"payoffs_{app.session_state['editor_version']}"]={'edited_rows':{4:{'Player 1':3.0}},'added_rows':[],'deleted_rows':[]}
    click(app,'Apply changes')
    assert app.session_state['game'].payoff('y','L','u')==3
    click(app,'Reset to original homework')
    assert app.session_state['game'].payoff('y','L','u')==0


def test_future_models_are_placeholders():
    app=open_app()
    next(r for r in app.radio if r.label=='Choose a model').set_value('Moral Hazard Model · coming later').run()
    assert any('Coming later' in i.value for i in app.info)
    assert not any(h.value=='The Maths Behind the Game' for h in app.header)
