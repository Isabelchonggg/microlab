"""Check topology and highlights so styling cannot silently alter the game."""
from models import homework_game
from visualization import game_tree, CHANCE, TYPE_NODES, RECEIVER_NODES, MINT, PINK, BLUE, CORAL
from solver import assess


def test_fixed_information_sets_and_eight_terminal_payoffs():
    g = homework_game()
    fig = game_tree(g, ("L", "R"), ("u", "d"))
    assert CHANCE[1] > TYPE_NODES['x'][1] == TYPE_NODES['y'][1]
    for shape, signal in zip(fig.layout.shapes, ('L', 'R')):
        assert shape.line.dash == 'dot'
        assert (shape.x0, shape.y0) == RECEIVER_NODES['x', signal]
        assert (shape.x1, shape.y1) == RECEIVER_NODES['y', signal]
    terminal_edges = [t for t in fig.data if '/' in (t.name or '') and ' → ' in (t.name or '')]
    assert len(terminal_edges) == 8
    terminals=[t for t in fig.data if (t.name or '').startswith('select:terminal:')]
    assert len(terminals)==8
    assert {t.text[0] for t in terminals} == {'(1, 1)','(2, 0)','(2, 2)','(0, 0)',
                                               '(0, 1)','(1, 0)'}
    assert {t.name for t in terminal_edges if t.line.color == BLUE} == {
        'x/L → u', 'y/L → u', 'x/R → d', 'y/R → d'}
    assert next(t for t in terminal_edges if t.name == 'y/L → u').line.dash == 'solid'
    assert all('Player 1:' in t.hovertemplate and 'Player 2:' in t.hovertemplate
               for t in terminals)


def test_equilibrium_colours_only_reached_paths_and_preserves_coordinates():
    normal = game_tree(homework_game(), ('R', 'R'), ('d', 'u'))
    revealed = game_tree(homework_game(), ('R', 'R'), ('d', 'u'), confirmed=True)
    assert normal.layout.shapes == revealed.layout.shapes
    assert [(tuple(t.x), tuple(t.y)) for t in normal.data] == [(tuple(t.x), tuple(t.y)) for t in revealed.data]
    assert {t.name for t in revealed.data if t.line.color == MINT} == {
        'x → R', 'y → R', 'x/R → u', 'y/R → u'}


def test_receiver_acts_identically_at_nodes_in_one_information_set_and_deviation_is_coral():
    fig = game_tree(homework_game(), ('R', 'L'), ('d', 'u'), deviations={('y', 'R')}, focus={'concept':'Equilibrium conclusion'})
    traces = {t.name: t for t in fig.data if t.name}
    assert traces['x/L → d'].line.color == traces['y/L → d'].line.color == BLUE
    assert traces['x/R → u'].line.color == BLUE
    assert traces['y → R'].line.color == CORAL
    assert traces['y → R'].line.dash == 'dash'
    assert traces['y/R → u'].line.color == BLUE


def test_both_tree_layouts_share_payoffs_and_expected_utility_focus():
    game=homework_game()
    candidate=assess(game,('L','R'),('u','d'))
    focus={'concept':'Expected utility','signal':'L','action':'u','kind':'x',
           'view_mode':'Trace one path','compare_actions':True}
    charts=[game_tree(game,candidate.sender,candidate.receiver,focus=focus,layout_style=style)
            for style in ('rectangular','branching')]
    for chart in charts:
        lines={trace.name:trace for trace in chart.data if trace.name}
        assert lines['x/L → u'].line.width==lines['x/L → d'].line.width==6
        assert lines['y/L → u'].line.width==lines['y/L → d'].line.width==6
        assert len([t for t in chart.data if (t.name or '').startswith('select:terminal:')])==8
    assert charts[0].layout.shapes[0].x0==charts[0].layout.shapes[0].x1
    assert charts[1].layout.shapes[0].y0==charts[1].layout.shapes[0].y1
