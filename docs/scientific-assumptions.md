# Scientific assumptions and units

## Scope of the executable baseline

- A **stationary** spherical cloud in a cube of equal diameter.
- Density is piecewise constant within cubic voxels.
- An external, **isotropic** boundary radiation field with intensity `I0`.
- One wavelength (grey optical coefficients), no polarization.
- Elastic scattering using the reciprocal Henyey-Greenstein phase function.
- Absorption removes photon weight; there is no thermal dust re-emission.
- Opacity per density unit is spatially constant: `alpha_abs(x) = rho(x)*kappa_abs`
  and `alpha_scat(x) = rho(x)*kappa_scat`.
- In the reverse estimator, random paths sample *scattering only*;
  absorption is accounted for by `exp(-integral alpha_abs ds)`.

The code does **not** simulate evolving gas, MHD, chemistry, or gamma interactions.

## Simulation units

No physical unit system is imposed. A typical benchmark uses a sphere radius of
1 length unit, density 1 density unit, opacity 1 per (length × density).
`kappa * integral(rho ds)` then produces dimensionless optical depth.
To add physical units, define a consistent input conversion and test it.

## Meaning of a directional map

`look_direction` points **away from the observer**, toward the source-side sky.
A physical photon from that sky direction propagates in the *opposite* direction.
The assumed external field is isotropic, so no external angular-source
transformation is needed. A future anisotropic/point-source implementation will
need a carefully specified boundary field evaluated in physical propagation
direction and validation tests.

We use uniform centers in `mu=cos(theta)` and `phi`, not uniform theta. Every
pixel therefore has the same solid angle; pixel averages approximate
`J=(1/4π)∫I dΩ` without extra sin(theta) weighting.

## Important comparisons

- `UncollidedSolver` computes `I0 * exp(-tau_ext)` where
  `tau_ext = integral((alpha_abs + alpha_scat) ds)`. **It omits scattered-in
  light** when scattering is present.
- `ReverseScatteringSolver` samples scattering events and weights paths by
  absorption. Its result estimates total directional intensity for the
  limited grey, reciprocal scattering model.
- With `kappa_scat = 0`, these solvers agree exactly for all directions.
- With `kappa_abs = 0`, the reverse solver returns exactly `I0` in an
  isotropically illuminated cloud, whatever the density, scattering optical
  depth, or scattering phase parameter (assuming all paths exit).

## What is deliberately *not* implemented

Mathis et al. (2002) hierarchical construction, full wavelength dependence,
external star sources, a forward solver, time-dependent cloud dynamics,
physical dust optical property tables, and gamma-ray interactions.

**Warning on gamma rays:** Gamma-ray Compton scattering changes photon energy;
pair production can generate secondary particles. Do not present the elastic
reverse estimator as a validated gamma-ray reverse/adjoint Monte Carlo method.
The course-project proposal mentions Geant4, but no Geant4 comparison has been
made in this scaffold.
