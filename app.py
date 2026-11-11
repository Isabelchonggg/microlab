"""MicroLab entry point. Add future models as separate page modules."""
import streamlit as st
from models import homework_game
from signalling_page import render_signalling_page
from moral_hazard_page import render_moral_hazard_page
from styling import CSS, MASCOT

st.set_page_config(page_title='MicroLab · my lil econ lab',page_icon='🌸',layout='wide')
st.markdown(CSS+MASCOT,unsafe_allow_html=True)
if 'game' not in st.session_state:
    st.session_state.game=homework_game()
    st.session_state.editor_version=0
for key, value in {
    'tree_sender': ('L','R'), 'tree_l': 'u', 'tree_r': 'u',
    'math_focus': 'Overview', 'focus_signal': 'L',
    'focus_action': 'u', 'focus_kind': 'x',
    'focus_compare_actions': False,
    'tree_view_mode': 'Full strategy',
}.items():
    if key not in st.session_state:
        st.session_state[key]=value
st.markdown('<div class="brand"><div class="brand-title">♡ MicroLab</div><div class="brand-sub">my lil econ lab</div></div>',unsafe_allow_html=True)
model=st.radio('Choose a model',('Signalling Model','Moral Hazard Model','Screening Model · coming later'),
               horizontal=True,label_visibility='collapsed')
if model=='Signalling Model':
    render_signalling_page()
elif model=='Moral Hazard Model':
    render_moral_hazard_page()
else:
    st.header(model)
    st.info('Coming later. The Signalling Model is ready to explore now.')
