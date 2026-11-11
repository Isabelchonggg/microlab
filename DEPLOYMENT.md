# Publish MicroLab with Streamlit Community Cloud

## Deployment settings

- GitHub repository: `Isabelchonggg/microlab`
- Visibility: public
- Branch: `main`
- Main file: `app.py`
- Python: **3.13** (the version used for local verification)
- Live app: https://isabelchonggg-microlab.streamlit.app/
- Secrets: none required

The repository and Streamlit Community Cloud deployment already exist. Cloud
reads the application directly from the repository's `main` branch.

## Update from VS Code after publication

1. Edit and save your files.
2. In the project terminal, activate the environment and test:

   ```bash
   source .venv/bin/activate
   python -m pytest -q
   ```

3. Open VS Code's **Source Control** panel. Review the changes, stage only
   intended project files with the **+** buttons, write a short message, then
   choose **Commit** and **Sync Changes**. Sign in to GitHub through VS Code
   if requested; never paste access tokens into chat.
4. Streamlit automatically updates the app from new commits pushed to `main`.
   Dependency changes may take a few minutes. Check the live page afterwards.

Equivalent terminal commands, after reviewing the diff:

```bash
git status
git diff
git add app.py signalling_page.py moral_hazard_model.py moral_hazard_visuals.py moral_hazard_page.py solver.py models.py visualization.py explanations.py styling.py requirements.txt tests .streamlit/config.toml README.md DEPLOYMENT.md .gitignore
git commit -m "Describe your MicroLab update"
git push origin main
```

VS Code may ask you to sign in to GitHub before the first sync from this machine.

## What is published

Only Python source, tests, requirements, documentation, `.gitignore` and the
pink `.streamlit/config.toml` theme belong in the repository. The original
seminar screenshot and unused overlay helper remain local. Virtual
environments, caches, `.env` files, private keys and `secrets.toml` are ignored.
Ignore rules do not protect secrets already tracked by Git: review every diff.
No OS-specific packages, local data files, API credentials or local absolute
paths are needed. Cloud installs its own environment from `requirements.txt`.
The SVG mascot is embedded in the source, and Helvetica uses local font
fallbacks without a remote font service.

## Check after deployment

- Open the actual public URL without a signed-in Streamlit session.
- Check the pink theme, both game trees, eight payoffs in each, and both information sets.
- Reveal a separating PBE and then a pooling PBE.
- Click a branch in each tree and confirm the strategy controls and maths update.
- Check the Intuitive Criterion explanation.
- Apply a payoff edit and reset the original game.
- Check phone width: controls and trees remain usable, with no clipped payoffs.
- Check Moral Hazard Q1–Q6, particularly Q5's optimal-contract ray and Q6's
  nonnegative-wage IC/IR graph, guided steps and linked clicks.

Reference: [Streamlit deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
and [automatic updates from GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/edit-your-app).
