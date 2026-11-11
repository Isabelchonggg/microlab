"""Pure Seminar 2 principal-agent calculations; no Streamlit or plotting imports."""
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Parameters:
    p_high: float = .9
    p_low: float = .7
    output_high: float = 100
    output_low: float = 0
    effort_cost: float = 1
    reservation: float = 3

    def __post_init__(self):
        if not (0 <= self.p_low < self.p_high <= 1):
            raise ValueError('Require 0 ≤ P(high output | low effort) < P(high output | high effort) ≤ 1.')
        if self.output_low < 0 or self.output_high < self.output_low:
            raise ValueError('Require 0 ≤ low output ≤ high output.')
        if self.effort_cost < 0 or self.reservation < 0:
            raise ValueError('Effort cost and reservation utility must be nonnegative.')

    @property
    def gap(self):
        return self.p_high - self.p_low

    def probability(self, effort):
        return self.p_high if effort == 'high' else self.p_low

    def output(self, effort):
        p = self.probability(effort)
        return p*self.output_high + (1-p)*self.output_low

    def cost(self, effort):
        return self.effort_cost if effort == 'high' else 0


@dataclass(frozen=True)
class Contract:
    w0: float
    w1: float
    effort: str
    utility_kind: str
    label: str = ''


def utility(wage, kind):
    if kind == 'sqrt':
        if wage < 0:
            raise ValueError('Square-root utility requires nonnegative wages.')
        return sqrt(wage)
    if kind == 'linear':
        return wage
    raise ValueError('Unknown utility kind.')


def expected_utility(params, contract, effort):
    p = params.probability(effort)
    return p*utility(contract.w1, contract.utility_kind) + (1-p)*utility(contract.w0, contract.utility_kind) - params.cost(effort)


def expected_profit(params, contract, effort):
    p = params.probability(effort)
    return p*(params.output_high-contract.w1)+(1-p)*(params.output_low-contract.w0)


def participation_slack(params, contract):
    return expected_utility(params, contract, contract.effort)-params.reservation


def incentive_slack(params, contract):
    other = 'low' if contract.effort == 'high' else 'high'
    return expected_utility(params, contract, contract.effort)-expected_utility(params, contract, other)


def feasible(params, contract, *, hidden=True, limited_liability=False):
    if contract.utility_kind == 'sqrt' and min(contract.w0, contract.w1) < 0:
        return False
    if limited_liability and min(contract.w0, contract.w1) < 0:
        return False
    if participation_slack(params, contract) < -1e-8:
        return False
    return not hidden or incentive_slack(params, contract) >= -1e-8


def full_information_contract(params, effort, *, worker_power=False):
    """Output-independent insurance; effort is verifiable under complete information."""
    if worker_power:
        wage = params.output(effort)
    else:
        wage = (params.reservation+params.cost(effort))**2
    return Contract(wage, wage, effort, 'sqrt', 'Full-information contract')


def risk_neutral_contracts(params, effort):
    """Representative optimal schedule, plus the full high-effort optimum ray."""
    if effort == 'low':
        w = params.reservation
        return Contract(w, w, effort, 'linear', 'Low-effort optimum')
    spread = params.effort_cost/params.gap
    expected_wage = params.reservation+params.effort_cost
    w0 = expected_wage-params.p_high*spread
    return Contract(w0, w0+spread, effort, 'linear', 'IC and IR binding')


def risk_averse_contracts(params, effort):
    """Global minimum wage cost for each prescribed effort with sqrt utility.

    For high effort write a=sqrt(w1), b=sqrt(w0). IC needs a-b>=c/d.
    If b=0 also meets IR, it is the cost minimum. Otherwise the unique
    minimum lies where IC and IR bind. This handles the sqrt domain exactly.
    """
    if effort == 'low':
        w = params.reservation**2
        return Contract(w, w, effort, 'sqrt', 'Low-effort full insurance')
    spread = params.effort_cost/params.gap
    required_utility = params.reservation+params.effort_cost
    if params.p_high == 1:
        a=max(required_utility,spread)
        return Contract(0,a*a,effort,'sqrt','High-output state is certain under high effort')
    b = max(0, required_utility-params.p_high*spread)
    a = b+spread
    return Contract(b*b, a*a, effort, 'sqrt',
                    'IC binding; IR '+('binding' if b > 1e-9 else 'may be slack'))


def optimal_hidden(params, kind):
    solve = risk_neutral_contracts if kind == 'linear' else risk_averse_contracts
    high, low = solve(params, 'high'), solve(params, 'low')
    high_profit = expected_profit(params, high, 'high')
    low_profit = expected_profit(params, low, 'low')
    winner = high if high_profit >= low_profit-1e-9 else low
    return winner, high, low


def scenario_result(params, question):
    """Returns the scenario's selected benchmark and comparison numbers."""
    if question == 1:
        high = full_information_contract(params, 'high')
        low = full_information_contract(params, 'low')
        return high if expected_profit(params, high, 'high') >= expected_profit(params, low, 'low') else low, high, low
    if question == 2:
        high = Contract(params.output_low, params.output_high, 'high', 'sqrt', 'Agent owns firm')
        low = Contract(params.output_low, params.output_high, 'low', 'sqrt', 'Agent owns firm')
        return high if expected_utility(params, high, 'high') >= expected_utility(params, low, 'low') else low, high, low
    if question == 3:
        high = full_information_contract(params, 'high', worker_power=True)
        low = full_information_contract(params, 'low', worker_power=True)
        return high if expected_utility(params, high, 'high') >= expected_utility(params, low, 'low') else low, high, low
    if question == 4:
        high = full_information_contract(params, 'high')
        low = full_information_contract(params, 'low')
        return high if expected_profit(params, high, 'high') >= expected_profit(params, low, 'low') else low, high, low
    if question == 5:
        return optimal_hidden(params, 'linear')
    if question == 6:
        return optimal_hidden(params, 'sqrt')
    raise ValueError('Question must be 1–6.')


def trade_is_worthwhile(params, question, high, low):
    """Compare the best conditional allocation with the no-trade outside option."""
    if question in (2,3):
        return max(expected_utility(params,high,'high'),
                   expected_utility(params,low,'low')) >= params.reservation-1e-8
    return max(expected_profit(params,high,'high'),
               expected_profit(params,low,'low')) >= -1e-8
