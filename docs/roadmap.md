# Suggested milestones / parallel group work

## M0 — Baseline sanity (already present)
- [x] Installable package and CLI
- [x] Uniform sphere and reproducible toy clumps
- [x] Piecewise-constant 3D voxel optical-depth ray tracing
- [x] Uncollided sky map (pure absorption when kappa_scat=0)
- [x] Minimal reverse elastic scattering + HG sampling
- [x] Tests and CI

## M1 — Validate the reverse elastic estimator
- [ ] Compare with an analytically or independently validated homogeneous
      sphere solution with both absorption and scattering (Bethell section 3.2).
- [ ] Convergence study: packets per direction, angular bins, grid resolution.
- [ ] More robust step/geometry tests and event-count benchmarks.
- [ ] Add benchmark results and confidence intervals.

## M2 — Realistic density structures
- [ ] Implement Mathis et al. 2002 section 2 hierarchical point-casting
      recipe in `clouds/hierarchical.py`, with periodic wrapping and
      a background option. Ensure reproducible seed and expected statistics.
- [ ] Normalize density to chosen mean central optical depth.
- [ ] Compare uniformly dense and clumpy clouds at **matched optical depth**.

## M3 — Physical observables / figures
- [ ] Position scans for `J(x)` and scatterplots of density vs intensity.
- [ ] Different optical depths, albedos, g, and wavelengths.
- [ ] Animated observer positions / sky maps.

## Optional M4 — Independent forward Monte Carlo
- [ ] Specify the SAME observable and estimator normalization first.
- [ ] Implement packet emission, scatter/absorb interactions, measurement tally.
- [ ] Compare statistical error vs wall-clock time at fixed target accuracy.

## Separate scope decision — Gamma rays / Geant4
- [ ] Ask the project team/instructor to resolve the gamma-ray vs UV/visible
      dust-scattering difference before investing in an inelastic gamma model.
- [ ] If gamma transport is required, specify photon energy range, source
      geometry, target material, opacity/cross-section data, secondary policies,
      and observable; validate forward physics before any adjoint work.
- [ ] Define how to account for reverse Compton energy kernels and energy
      Jacobians. Bethell's elastic reverse paths are **not sufficient**.
