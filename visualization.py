"""Fixed-coordinate extensive-form tree; rendering does not calculate equilibrium.

Every selected path, belief focus and payoff focus comes from the same caller
selection. The two nodes in each receiver information set share one action.
"""
import plotly.graph_objects as go
from explanations import number
from models import ACTIONS, SIGNALS, TYPES

FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif'
PINK, MINT, LAVENDER, INK = '#DC2626', '#16803D', '#C9C9C9', '#171717'
X, Y, BLUE, BELIEF, CORAL = INK, INK, '#2563EB', INK, PINK
CHANCE = (.5, .96)
TYPE_NODES = {'x': (.25, .78), 'y': (.75, .78)}
RECEIVER_NODES = {('x','L'):(.10,.55), ('y','L'):(.64,.55),
                  ('x','R'):(.36,.43), ('y','R'):(.90,.43)}


def game_tree(game, sender, receiver, *, confirmed=False, deviations=(), focus=None,
              compact=False, layout_style='branching'):
    """Draw all eight terminals with stable information sets and linked focus."""
    if layout_style not in ('branching','rectangular'):
        raise ValueError('Unknown tree layout')
    rectangular=layout_style=='rectangular'
    chance=(.5,.5) if rectangular else CHANCE
    type_nodes={'x':(.5,.8),'y':(.5,.2)} if rectangular else TYPE_NODES
    receiver_nodes=({('x','L'):(.23,.8),('x','R'):(.77,.8),
                     ('y','L'):(.23,.2),('y','R'):(.77,.2)}
                    if rectangular else RECEIVER_NODES)
    fig = go.Figure()
    annotations = []
    responses = dict(zip(SIGNALS, receiver))
    deviations = set(deviations)
    focus = focus or {}
    concept = focus.get('concept', 'Overview')
    target_signal = focus.get('signal', 'L')
    target_action = focus.get('action', 'u')
    compare_actions = focus.get('compare_actions', False)
    target_kind = focus.get('kind', 'x')
    trace_mode = focus.get('view_mode') == 'Trace one path'
    focused = concept != 'Overview'
    sender_for = dict(zip(TYPES, sender))

    def label(x, y, text, size=14, color=INK, *, important=False):
        annotations.append(dict(x=x, y=y, text=f'<b>{text}</b>' if important else text,
                                showarrow=False, font=dict(size=size-2 if compact else size, color=color),
                                bgcolor='white', borderpad=3))

    def edge(start, end, selected, name, *, reached=True, role='sender',
             relevant=False, hypothetical=False):
        color = (INK if role == 'chance' and relevant else PINK if hypothetical else MINT if confirmed and selected and reached else
                 (BLUE if role == 'receiver' else PINK) if selected else LAVENDER)
        opacity = 1 if not focused and not trace_mode or relevant or hypothetical else .28
        fig.add_trace(go.Scatter(x=[start[0], end[0]], y=[start[1], end[1]],
            mode='lines', name=name, opacity=opacity,
            line=dict(color=color, width=6 if relevant else 5 if selected or hypothetical else 2,
                      dash='dash' if hypothetical else 'solid'),
            hovertemplate=name + (' · hypothetical deviation' if hypothetical else
                                  ' · off path' if not reached else '') + '<extra></extra>',
            showlegend=False))

    def node(position, name, *, relevant=False):
        fig.add_trace(go.Scatter(x=[position[0]], y=[position[1]], mode='markers',
            name=name, marker=dict(size=16 if relevant else 12, color=INK,
                                   line=dict(color='white', width=2)),
            opacity=1 if not focused and not trace_mode or relevant else .38,
            hovertemplate=name+'<extra></extra>', showlegend=False))

    def branch_target(position, text, target, selected, role):
        """A visible Plotly point makes the branch selectable by a click or tap."""
        fig.add_trace(go.Scatter(x=[position[0]], y=[position[1]],
            mode='markers+text', text=[text], textposition='middle center',
            textfont=dict(family=FONT, size=12 if compact else 14, color=INK), name=target,
            marker=dict(size=25 if compact else 29, color='white',
                        line=dict(color=(PINK if role == 'sender' else BLUE) if selected else '#B8B8B8',
                                  width=2.5 if selected else 1)),
            hovertemplate=f'Click to choose {text}<extra></extra>', showlegend=False))

    # Information sets remain dotted, including when focus dims other paths.
    for signal in SIGNALS:
        left=receiver_nodes['x',signal]
        right=receiver_nodes['y',signal]
        relevant = focused and concept in ('Beliefs','Expected utility','Receiver best responses') and signal == target_signal
        fig.add_shape(type='line', x0=left[0], x1=right[0], y0=left[1], y1=right[1],
                      line=dict(color=BELIEF, width=4 if relevant else 2.5, dash='dot'),
                      opacity=1 if relevant or not focused else .45)
        label(left[0] if rectangular else (left[0]+right[0])/2,
              (left[1]+right[1])/2 if rectangular else left[1]+.025,
              f'<b>Player 2 sees {signal}</b><br>type unknown' if rectangular else
              f'<b>Player 2 sees {signal}</b> · type unknown', 11)
    node(chance, 'Chance', relevant=concept == 'Beliefs')
    label(.5, .5 if rectangular else 1.015, '<b>Nature</b>', 16)

    for kind in TYPES:
        chosen = sender_for[kind]
        position = type_nodes[kind]
        chance_relevant = (trace_mode and kind == target_kind) or (concept == 'Beliefs' and chosen == target_signal) or (
            concept == 'Expected utility' and chosen == target_signal) or (
            concept == 'Sender incentive constraints' and kind == target_kind)
        edge(chance, position, False, f'Chance → {kind}', role='chance', relevant=chance_relevant)
        probability = game.prior if kind == 'x' else 1-game.prior
        label((position[0]+chance[0])/2+(.055 if rectangular else 0),
              (position[1]+chance[1])/2+(.025 if not rectangular else 0),
              f"{kind}: {str(number(probability)).replace('1/2', '½')}", 13)
        node(position, f'Player 1 · type {kind}',
             relevant=concept == 'Sender incentive constraints' and kind == target_kind)
        label(position[0], position[1]+(.04 if kind=='x' or not rectangular else -.04),
              f'<b>Player 1 · {kind}</b>')
        for signal in SIGNALS:
            receiver_node = receiver_nodes[kind, signal]
            reached = chosen == signal
            sender_relevant = (
                concept == 'Beliefs' and reached and signal == target_signal or
                concept == 'Expected utility' and reached and signal == target_signal or
                concept == 'Receiver best responses' and reached and signal == target_signal or
                concept == 'Sender incentive constraints' and kind == target_kind or
                 concept == 'Equilibrium conclusion' and reached or
                 trace_mode and kind == target_kind and signal == target_signal)
            hypothetical = (concept == 'Sender incentive constraints' and
                            kind == target_kind and not reached) or (
                            concept == 'Equilibrium conclusion' and (kind,signal) in deviations and not reached)
            edge(position, receiver_node, reached, f'{kind} → {signal}',
                 relevant=sender_relevant, hypothetical=hypothetical)
            branch_target(((position[0]+receiver_node[0])/2, position[1]),
                          signal, f'select:sender:{kind}:{signal}', reached, 'sender')
            receiver_relevant = (concept in ('Beliefs','Expected utility','Receiver best responses') and
                                 signal == target_signal) or (
                                 concept == 'Sender incentive constraints' and kind == target_kind) or (
                                 trace_mode and kind == target_kind and signal == target_signal)
            node(receiver_node, f'Player 2 · {kind}/{signal}', relevant=receiver_relevant)
            for action in ACTIONS:
                terminal = ((.035 if signal=='L' else .965,
                             position[1]+(.115 if action=='u' else -.115)) if rectangular else
                            (receiver_node[0]+(-.06 if action=='u' else .06),
                             .30 if signal=='L' else .11))
                selected = responses[signal] == action
                if concept == 'Expected utility':
                    action_relevant = signal == target_signal and (compare_actions or action == target_action)
                elif concept == 'Receiver best responses':
                    action_relevant = signal == target_signal
                elif concept == 'Sender incentive constraints':
                    action_relevant = kind == target_kind and selected
                elif concept == 'Equilibrium conclusion':
                    action_relevant = reached and selected
                else:
                    action_relevant = False
                action_relevant = action_relevant or (trace_mode and kind == target_kind and
                    signal == target_signal and action == target_action)
                edge(receiver_node, terminal, selected, f'{kind}/{signal} → {action}',
                     reached=reached, role='receiver', relevant=action_relevant)
                branch_target(((receiver_node[0]+terminal[0])/2,
                               (receiver_node[1]+terminal[1])/2), action,
                              f'select:receiver:{kind}:{signal}:{action}', selected, 'receiver')
                pair = game.payoffs[kind, signal, action]
                payoff_relevant = (concept == 'Expected utility' and signal == target_signal and
                                   (compare_actions or action == target_action)) or (
                                   concept == 'Receiver best responses' and signal == target_signal) or (
                                   concept == 'Sender incentive constraints' and kind == target_kind and selected) or (
                                   concept == 'Equilibrium conclusion' and reached and selected)
                payoff_relevant = payoff_relevant or (trace_mode and kind == target_kind and
                    signal == target_signal and action == target_action)
                payoff_color = (BLUE if concept in ('Expected utility','Receiver best responses') else
                                PINK if concept == 'Sender incentive constraints' else
                                MINT if confirmed and payoff_relevant else INK) if payoff_relevant else (
                                '#A8A8A8' if focused else INK)
                fig.add_trace(go.Scatter(x=[terminal[0]], y=[terminal[1]], mode='markers+text',
                     text=[f'({number(pair[0])}, {number(pair[1])})'],
                     textposition='middle center',
                     textfont=dict(family=FONT,size=12 if compact else 15,color=payoff_color),
                     name=f'select:terminal:{kind}:{signal}:{action}',
                     marker=dict(size=45 if compact else 57,color='white',
                                 line=dict(color=payoff_color if payoff_relevant else '#B8B8B8',
                                           width=3 if payoff_relevant else 1)),
                     opacity=1 if not trace_mode or payoff_relevant else .4,
                     showlegend=False,
                     hovertemplate=(f'Type {kind} · {signal} → {action}<br>'
                                    f'Player 1: {number(pair[0])}<br>Player 2: {number(pair[1])}<extra></extra>')))
    fig.update_layout(height=510 if compact else 680, margin=dict(l=4 if compact else 12, r=4 if compact else 12, t=8, b=8),
        paper_bgcolor='white', plot_bgcolor='white', annotations=annotations,
        xaxis=dict(range=[-.045, 1.045], visible=False, fixedrange=True),
        yaxis=dict(range=[-.02, 1.02] if rectangular else [.01, 1.06], visible=False, fixedrange=True),
        font=dict(family=FONT, color=INK), dragmode=False, clickmode='event+select')
    return fig
