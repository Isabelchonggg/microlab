# ♡ MicroLab — Advanced Microeconomics study lab

MicroLab is a Streamlit study app with linked visual modules for Seminar 3 Signalling and Seminar 2 Moral Hazard. Screening remains a future module.

## Run locally

From this project folder in VS Code’s terminal:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Stop the server with Ctrl+C. On a fresh machine, create the environment first with `python3 -m venv .venv`.

## Explore the model

At the top of the Signalling Model page, click one of four visible Player 1 candidate strategies and select Player 2’s responses after L and R independently. Two fixed-coordinate, clickable Python game trees update together: a compact rectangular tree and a traditional branching tree. Click a branch or payoff in either tree to update the shared strategy and mathematical focus. Red marks sender choices and hypothetical deviations; blue marks receiver actions; green marks a solver-confirmed equilibrium; black marks beliefs and labels. Unselected branches are grey. The dotted information sets always remain visible.

**Show equilibrium ♡** checks the selected candidate. If it has one supported receiver profile, the button selects and highlights that response. If it has multiple supported profiles, the page displays all alternatives and their valid belief intervals; choose one explicitly to highlight it. Changing a manual control clears the green confirmation. The status indicators distinguish manual selection, receiver best responses, sender incentives, and PBE status.

The original seminar screenshot and overlay are not displayed or needed for deployment. They remain local-only reference material.


“The Maths Behind the Game” updates automatically and displays strategy classification, Bayesian beliefs, expected payoffs and substitutions, receiver best responses, sender incentives, the PBE verdict, and the Intuitive Criterion when supported. Select one of its five mathematical cards, then choose a signal, action, or sender type. The tree dims unrelated paths and emphasises the information set, branches, and payoff pairs used in that calculation. The solver checks 16 pure strategy profiles and exact off-path belief intervals. For the original homework, the tested Intuitive Criterion proof covers the separating equilibrium and pooling-on-R equilibria. The app does not claim a general Intuitive Criterion result for arbitrary edited games.

At the bottom, edit Nature’s prior or any terminal payoff pair and click **Apply changes**. The page recalculates from the edited game. **Reset to original homework** restores all original values. Edits live in the current Streamlit session.

## Explore Moral Hazard

Choose **Moral Hazard Model**, then select Seminar 2 question Q1–Q6. The decision tree and mathematical graph stay visible together. Q1–Q4 use observable, contractible effort; Q5–Q6 use hidden effort and an output-contingent wage schedule. Q5 changes utility to linear and permits negative wages. Q6 uses square-root utility and nonnegative wages.

Edit probabilities, outputs, cost, reservation utility and proposed wages to recalculate the tree, graph, incentive and participation checks, and profit comparison. Clicking an effort, terminal, constraint or equation focuses its linked calculation. **Show optimal contract** displays the best computed contract separately from the user's proposal. **Solve with me** reveals the derivation one step at a time. The Q6 solver respects the square-root domain: with the original values its high-effort optimum is \(w_0=0,w_1=25\), with IC binding and IR slack.

## Code structure

| File | Purpose |
| --- | --- |
| `app.py` | Branding and model-based navigation. Add future model pages here. |
| `signalling_page.py` | The one-page Signalling Model controls and workings. |
| `models.py` | Exact game data and validation. |
| `solver.py` | Bayes’ rule, best responses, incentives, PBE enumeration, and scoped Intuitive Criterion proof. |
| `visualization.py` | Two fixed-coordinate Plotly game-tree layouts with all information sets and payoff pairs. |
| `math_display.py` | Typeset equations and step-by-step presentation. |
| `styling.py` | Helvetica, four pen colours, cards, and bunny mascot. |
| `moral_hazard_model.py` | Pure Seminar 2 expected utility, profit, feasibility, and six-scenario solutions. |
| `moral_hazard_visuals.py` | Clickable principal–agent tree and question-specific mathematical graphs. |
| `moral_hazard_page.py` | Shared Moral Hazard controls, linked maths, and guided solving. |
| `tests/` | Mathematical, focused-diagram, and Streamlit interaction checks. |

The economic calculations are separate from Streamlit styling and diagram rendering. Screening can be added without changing either existing solver.

## Verify

```bash
python -m pytest -q
```

The public deployment follows the `main` branch of the GitHub repository.
