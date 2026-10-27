# Collaborating on this repository

## One-time local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.
Use Python 3.11+ (CI checks 3.11, 3.12, and 3.13).

## Working on a feature

1. Start from a current `main`: `git switch main && git pull`.
2. Create a focused branch: `git switch -c feat/hierarchical-cloud`.
3. Implement a small, reviewable change, with tests and documented physics.
4. Run `ruff check .`, `ruff format --check .`, and `pytest -q` locally.
   You can autoformat with `ruff format .` and fix safe lint changes with
   `ruff check --fix .`.
5. Commit and push: `git add . && git commit -m "Add hierarchical cloud"`
   then `git push -u origin feat/hierarchical-cloud`.
6. Open a pull request, link the issue, and request **at least one teammate
   review** before merging. Do not commit directly to `main`.

## Shared standards

- Use `snake_case` for functions/files, `PascalCase` for classes.
- Prefer small pure functions with units, shape, and assumptions in docstrings.
- Use `numpy.random.default_rng(seed)` and pass the generator, never global
  `np.random.seed(...)`; every experiment saves its seed and config.
- Do not edit an unrelated teammate's module without discussing the API.
- Do not silently replace an exact scientific method with an approximation.
- Avoid committing generated `outputs/`, data cubes, or virtual environments.
- Compare at matched mean optical depth before claiming a clumping effect.
- Save equation references and note every meaningful physical approximation.
- Benchmarks should record time, machine, uncertainty, and grid/packet count.

## Repo settings a team admin should enable on GitHub

- Protect the `main` branch (or create a ruleset).
- Require pull requests and **one approving review**.
- Require all `tests` CI matrix checks before merging.
- Block force pushes to `main`.
- Enable Issues and assign ownership of milestones from `docs/roadmap.md`.

No remote repo or team permissions are created by this scaffold.
