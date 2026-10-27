# PHYS 332 — Monte Carlo Radiative Transfer

A modular Python research codebase for simulating direction-dependent
radiation inside a structured molecular cloud. The runnable baseline
uses **single-wavelength elastic dust scattering** in a spherical cloud
with an **isotropic external radiation field**, following the conceptual
setup of Bethell et al. (2004), Appendix A.

> **Scope:** The team's draft proposal also discusses gamma rays and
> Geant4. Those involve *different physics* (inelastic Compton scattering,
> pair production, etc.). They are intentionally **not implemented** here.
> Resolve this with your professor/team before treating this as a gamma
> transport code. See [scientific assumptions](docs/scientific-assumptions.md).

## Quick start (Python 3.11+)

```bash
git clone <YOUR-REPO-URL>
cd phys332-radiative-transfer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

rtmc check-config -c configs/baseline.toml
rtmc run -c configs/baseline.toml -o outputs/baseline
rtmc run -c configs/clumpy_reverse.toml -o outputs/clumpy_reverse
pytest -q
ruff check .
ruff format --check .
```

Windows activation: `.venv\\Scripts\\Activate.ps1` (PowerShell).
`python -m rtmc ...` also works if a terminal doesn't find `rtmc`.

## Outputs

Each run saves the config/seed/summary in `metadata.json` and the following
files to the chosen `outputs/` directory (which is gitignored):

- `sky_map.npz` — `mu`, `phi`, directional `intensity`, and `stderr` arrays
- `sky_map.png` — equirectangular sky map from the observer
- `density_slice.png` — a slice of the input 3D cloud

`mu=cos(theta)` and azimuth bins are equal-solid-angle, so their arithmetic
mean approximates the all-sky mean intensity `J`.

The baseline is analytically checkable: for the observer at the center of a
uniform sphere with pure absorption, `J/I0 = exp(-kappa_abs*rho*R) = exp(-1)`.

## Repository layout

```text
.
├── .github/               # Pull request template, feature issues, CI
├── configs/               # Version-controlled, reproducible experiments
├── docs/                  # Architecture, scientific assumptions, roadmap
├── experiments/           # Markdown logs (not large result arrays)
├── src/rtmc/
│   ├── clouds/            # DensityGrid, uniform and toy clumped models
│   ├── physics/           # Optical coefficients, Henyey-Greenstein phase
│   ├── transport/         # DDA ray tracing, direct and reverse estimators
│   ├── observables/       # Direction bins and sky-map estimators
│   ├── visualization/     # Figures, no solver logic
│   ├── io/                # Reproducible saved output
│   ├── config.py          # TOML configuration + validation
│   ├── simulation.py      # Pure simulation orchestrator
│   └── cli.py             # `rtmc` command
└── tests/                 # Scientific and package tests
```

## Implemented versus TODO

| Working now | To be implemented/tested |
|---|---|
| Uniform sphere; Gaussian-clump toy cloud | Paper-exact Mathis hierarchical clouds |
| Exact voxel-segment optical-depth integrals | Wavelength-dependent dust optical tables |
| Uncollided/pure-absorption solver | Validated full scattering benchmark of Bethell |
| Initial reverse elastic-scattering estimator | Independent forward Monte Carlo |
| HG random scattering directions | Point sources and anisotropic boundary light |
| Sky maps, mean intensity, output figures | Camera fly-through, resolution/MC convergence |
| Unit tests and CI | Gamma-ray/Geant4 work (separate research scope) |

**Do not interpret the presence of a working algorithm as full scientific
validation.** See [roadmap](docs/roadmap.md) for missing convergence and
benchmark work.

## Publish the downloaded scaffold as a shared GitHub repo

Once you unzip the starter project locally, the directory is **not** connected
to GitHub yet. From inside it, you can initialize and publish it with the
[GitHub CLI](https://cli.github.com/) (after authenticating with `gh auth login`):

```bash
git init -b main
git add .
git commit -m "Initial PHYS 332 scaffold"
gh repo create phys332-radiative-transfer --private --source=. --remote=origin --push
```

Invite your teammates through GitHub's **Settings → Collaborators** (or use
an organization repository), then enable branch rules as outlined below.
If you prefer the GitHub website, create an **empty** private repository
(without initializing a README), add its URL as `origin`, and push `main`.

## Group work / code reviews

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening PRs. Use short feature
branches, tests, and at least one reviewer; protect `main` and require CI on
GitHub. The [architecture guide](docs/architecture.md) explains where new
features belong and how to prevent accidental cross-module coupling.

## Scientific references

- Bethell et al. (2004), *Dust Heating by the Interstellar Radiation Field in
  Models of Turbulent Molecular Clouds*. Appendix A for reverse ray tracing.
- Mathis, Whitney & Wood (2002), *Can Reflection from Grains Diagnose the Albedo?*
  Section 2 for hierarchical test-cloud construction.

See [references](docs/references.md) for the specific roles of each paper.
