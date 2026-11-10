# ♡ MicroLab — Signalling Model

MicroLab is a Streamlit study app for Advanced Microeconomics Seminar 3. It has one scrollable Signalling Model page. Moral Hazard and Screening appear in navigation as future modules; neither is implemented yet.

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
| `tests/` | Mathematical, focused-diagram, and Streamlit interaction checks. |

The economic calculations are separate from Streamlit styling and tree rendering. Future Moral Hazard and Screening models can be added as new page modules without changing the signalling solver.

## Verify

```bash
python -m pytest -q
```

The public deployment follows the `main` branch of the GitHub repository.
