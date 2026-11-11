"""Plotly views of one moral-hazard model state; no optimization lives here."""
from math import sqrt
import plotly.graph_objects as go
from moral_hazard_model import expected_utility, expected_profit, utility

RED, BLUE, GREEN, BLACK, GREY = '#DC2626', '#2563EB', '#16803D', '#171717', '#B8B8B8'
FONT = '"Helvetica Neue",Helvetica,Arial,sans-serif'


def _base(fig, height=460):
    fig.update_layout(height=height, margin=dict(l=22,r=20,t=28,b=35),
                      paper_bgcolor='white', plot_bgcolor='white',
                      font=dict(family=FONT,color=BLACK,size=12),
                      clickmode='event+select', dragmode=False,
                      legend=dict(orientation='h',y=-.17,x=0))
    return fig


def decision_tree(params, contracts, selected_effort, focus='', *, hidden=False):
    """Offer → accept/reject → effort → chance → four wage/output outcomes."""
    fig = go.Figure()
    def line(a,b,color=GREY,width=2,dash='solid'):
        fig.add_trace(go.Scatter(x=[a[0],b[0]],y=[a[1],b[1]],mode='lines',
                     line=dict(color=color,width=width,dash=dash),showlegend=False,
                     hoverinfo='skip'))
    def point(pos,text,name,color=BLACK,size=12,hover=None,selected=False):
        fig.add_trace(go.Scatter(x=[pos[0]],y=[pos[1]],mode='markers+text',
                     text=[text],textposition='top center',textfont=dict(size=size,color=color),
                     marker=dict(size=14 if selected else 9,color=color),
                     name=name,showlegend=False,
                     hovertemplate=(hover or text)+'<extra></extra>'))
    root=(.5,.96); accept=(.5,.82); reject=(.08,.78); effort=(.5,.66)
    line(root,accept,BLUE,4); line(root,reject,GREY)
    point(root,'Principal offers wages','offer',BLUE,12)
    point(accept,'Agent: accept?','accept',BLACK)
    point(reject,'Reject · U = '+f'{params.reservation:g}','reject',BLACK)
    line(accept,effort,BLACK); point(effort,'Choose effort','choice',BLACK)
    for e,x in [('high',.24),('low',.76)]:
        contract=contracts[e]
        choice=(x,.49)
        chosen=e==selected_effort
        emphasize=focus in ('effort_'+e,'ic') or chosen and focus in ('profit','optimal')
        line(effort,choice,RED if chosen or emphasize else GREY,5 if emphasize else 4 if chosen else 2)
        point(((x+.5)/2,.59),'High effort' if e=='high' else 'Low effort',
              'effort_'+e,RED if emphasize or chosen else BLACK,11,
              hover=f'Click to inspect {e} effort',selected=emphasize)
        point(choice,'Nature', 'nature_'+e,BLACK)
        p=params.probability(e)
        for outcome,dx,prob,wage,output in (
            ('high',-.14,p,contract.w1,params.output_high),
            ('low',.14,1-p,contract.w0,params.output_low)):
            terminal=(x+dx,.17)
            line(choice,terminal,BLUE if focus in ('wage','ir') else GREEN if chosen and focus=='optimal' else GREY,
                 4 if focus in ('wage','ir','optimal') and chosen else 2)
            agent=utility(wage,contract.utility_kind)-params.cost(e)
            profit=output-wage
            label=(f'Q={output:g}<br>w={wage:.2f}<br>'
                   f'U={agent:.2f}<br>π={profit:.2f}')
            target=f'outcome_{e}_{outcome}'
            point(terminal,label,target,GREEN if focus==target else BLACK,10,
                  hover=f'{e.title()} effort, {outcome} output<br>Probability {prob:.2f}'
                        f'<br>Output {output:g}; wage {wage:.2f}'
                        f'<br>Agent utility {agent:.3f}; principal profit {profit:.3f}',
                  selected=focus==target)
            fig.add_annotation(x=(x+terminal[0])/2,y=.34,text=f'{prob:.2f}',
                               showarrow=False,font=dict(size=11,color=BLACK))
    note=('Hidden effort · wages depend on output only' if hidden else
          'Observable effort · enforceable effort-contingent offers')
    fig.add_annotation(x=.5,y=.02,text=note,showarrow=False,
                       font=dict(size=11,color=BLACK),bgcolor='white')
    _base(fig)
    fig.update_xaxes(range=[-.05,1.05],visible=False,fixedrange=True)
    fig.update_yaxes(range=[0,1.04],visible=False,fixedrange=True)
    return fig


def contract_graph(params, question, proposed, optimum, high, low, focus='',trade=True,
                   show_optimal=True,selected_effort=None):
    """Question-specific mathematical view computed from the same contracts."""
    fig=go.Figure()
    if question in (1,2):
        if question==1:
            ys=[expected_profit(params,high,'high'),expected_profit(params,low,'low')]
            title='Net value under insured effort'; unit='Output − participation wage'
        else:
            ys=[expected_utility(params,high,'high'),expected_utility(params,low,'low')]
            title='Residual claimant: expected utility'; unit='Agent utility'
        for effort,y in zip(('high','low'),ys):
            fig.add_trace(go.Bar(x=[effort.title()],y=[y],name='effort_'+effort,
                marker_color=RED if focus=='effort_'+effort else GREEN if show_optimal and trade and optimum.effort==effort else BLUE,
                hovertemplate=f'{effort.title()} effort<br>{unit}: {y:.3f}<extra></extra>'))
        if question==1:
            proposed_value=expected_profit(params,proposed,proposed.effort)
            fig.add_trace(go.Scatter(x=[proposed.effort.title()],y=[proposed_value],
                mode='markers',name='proposed',marker=dict(size=15,color=BLUE,symbol='diamond'),
                hovertemplate=f'Your proposed wages<br>{unit}: %{{y:.3f}}<extra></extra>'))
        fig.update_yaxes(title=unit, rangemode='tozero')
        fig.update_layout(title=title,showlegend=False)
    elif question in (3,4):
        upper=max(110,params.output_high*1.15,(params.reservation+params.effort_cost)**2*1.3)
        xs=[upper*i/100 for i in range(101)]
        fig.add_trace(go.Scatter(x=xs,y=[sqrt(w) for w in xs],mode='lines',
             name='Utility √w',line=dict(color=BLUE,width=3),
             hovertemplate='Wage %{x:.2f}<br>Utility √w = %{y:.3f}<extra></extra>'))
        for e,c in (('high',high),('low',low)):
            fig.add_trace(go.Scatter(x=[c.w1],y=[sqrt(c.w1)-params.cost(e)],
                mode='markers+text',text=[e.title()+' effort'],textposition='top center',
                marker=dict(size=15,color=GREEN if show_optimal and trade and optimum.effort==e else RED),name='effort_'+e,
                hovertemplate=f'{e.title()} effort<br>Constant wage {c.w1:.3f}'
                              f'<br>Agent utility %{{y:.3f}}<extra></extra>'))
        proposed_wage=(params.probability(proposed.effort)*proposed.w1+
                       (1-params.probability(proposed.effort))*proposed.w0)
        fig.add_trace(go.Scatter(x=[proposed_wage],
            y=[expected_utility(params,proposed,proposed.effort)],mode='markers',
            name='proposed',marker=dict(size=15,color=BLUE,symbol='diamond'),
            hovertemplate='Your proposed contract<br>Expected wage %{x:.2f}'
                          '<br>Expected agent utility %{y:.3f}<extra></extra>'))
        fig.add_hline(y=params.reservation,line_dash='dot',line_color=BLACK,
                      annotation_text='Reservation utility')
        fig.update_xaxes(title='Certain wage, w',range=[0,upper])
        fig.update_yaxes(title='Utility √w − effort cost')
        fig.update_layout(title='Full-information wage and risk sharing')
    else:
        kind='linear' if question==5 else 'sqrt'
        inspected=selected_effort or proposed.effort
        p=params.probability(inspected)
        needed=params.reservation+params.cost(inspected)
        if kind=='linear':
            lo=min(-8,proposed.w0-3,high.w0-3)
            hi=max(18,proposed.w0+5,low.w0+5)
        else:
            lo=0
            hi=max(6,proposed.w0+3,high.w0+6,low.w0+3 if inspected=='low' else 0)
        xs=[lo+(hi-lo)*i/100 for i in range(101)]
        def ir(x):
            if kind=='linear':
                return (needed-(1-p)*x)/p
            rhs=(needed-(1-p)*sqrt(x))/p
            return max(0,rhs)**2
        def ic(x):
            return x+params.effort_cost/params.gap if kind=='linear' else (sqrt(x)+params.effort_cost/params.gap)**2
        ir_y=[ir(x) for x in xs]; ic_y=[ic(x) for x in xs]
        max_y=max(36,max(proposed.w1,high.w1,low.w1)*1.35)
        if kind=='sqrt': max_y=max(max_y,ic(hi)*1.1)
        if inspected=='high':
            floor=[max(ir_y[i],ic_y[i]) for i in range(len(xs))]
            fig.add_trace(go.Scatter(x=xs,y=floor,mode='lines',line=dict(width=0),
                     showlegend=False,hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=xs,y=[max_y]*len(xs),fill='tonexty',
                     fillcolor='rgba(22,128,61,.09)',line=dict(width=0),
                     name='High-effort feasible region',hoverinfo='skip'))
        else:
            valid=[i for i in range(len(xs)) if ir_y[i]<=ic_y[i]+1e-9]
            polygon_x=[xs[i] for i in valid]+[xs[i] for i in reversed(valid)]
            polygon_y=[ir_y[i] for i in valid]+[ic_y[i] for i in reversed(valid)]
            fig.add_trace(go.Scatter(x=polygon_x,y=polygon_y,fill='toself',
                fillcolor='rgba(22,128,61,.09)',line=dict(width=0),
                name='Low-effort feasible region',hoverinfo='skip'))
        for name,ys,color in [('IR',ir_y,BLUE),('IC',ic_y,RED)]:
            fig.add_trace(go.Scatter(x=xs,y=ys,mode='lines+markers',
                 marker=dict(size=7,opacity=.25),name=name,
                 line=dict(color=color,width=5 if focus.lower()==name.lower() else 2.5),
                 hovertemplate=f'{name} boundary<br>w₀=%{{x:.2f}}, w₁=%{{y:.2f}}<extra></extra>'))
        benchmark=high if inspected=='high' else low
        budget=p*benchmark.w1+(1-p)*benchmark.w0
        iso=[(budget-(1-p)*x)/p for x in xs]
        fig.add_trace(go.Scatter(x=xs,y=iso,mode='lines+markers',name='Isoprofit',
             line=dict(color=BLACK,dash='dot',width=3 if focus=='profit' else 2),
             marker=dict(size=7,opacity=.2),hovertemplate='Equal expected wage / profit<extra></extra>'))
        if question==5 and show_optimal:
            ray=[x for x in xs if x<=high.w0]
            fig.add_trace(go.Scatter(x=ray,y=[ir(x) for x in ray],mode='lines+markers',
                name='Optimal contracts',line=dict(color=GREEN if trade and optimum.effort=='high' else GREY,width=5),
                marker=dict(size=3,opacity=.1),
                hovertemplate='Optimal high-effort contract<br>w₀=%{x:.2f}, w₁=%{y:.2f}<extra></extra>'))
        points=[('Proposed contract',proposed,BLUE)]
        if show_optimal:
            points.insert(0,('Optimal high effort' if trade and optimum.effort=='high' else 'Best conditional high effort',
                             high,GREEN if trade and optimum.effort=='high' else GREY))
        for name,c,color in points:
            fig.add_trace(go.Scatter(x=[c.w0],y=[c.w1],mode='markers+text',
                text=[name],textposition='top right' if c is high else 'bottom right',
                name='optimal' if c is high else 'proposed',
                marker=dict(size=15,color=color),
                hovertemplate=f'{name}<br>w₀=%{{x:.3f}}, w₁=%{{y:.3f}}<extra></extra>'))
        if show_optimal or inspected=='low':
            fig.add_trace(go.Scatter(x=[low.w0],y=[low.w1],mode='markers+text',
                text=['Global low-effort optimum' if show_optimal and trade and optimum.effort=='low' else 'Low-effort benchmark'],
                textposition='top right',name='optimal_low',
                marker=dict(size=18 if focus=='effort_low' else 14,
                            color=RED if focus=='effort_low' else GREEN if show_optimal and trade and optimum.effort=='low' else GREY),
                hovertemplate='Low-effort contract<br>w₀=%{x:.3f}, w₁=%{y:.3f}<extra></extra>'))
        fig.update_xaxes(title='Low-output wage, w₀',range=[lo,hi])
        fig.update_yaxes(title='High-output wage, w₁',range=[min(-3,lo) if kind=='linear' else 0,max_y])
        fig.update_layout(title=f'Hidden-action wage space · {inspected} effort')
    return _base(fig)
