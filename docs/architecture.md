# Architecture and boundaries between components

```text
config.toml → config.py → simulation.py
                           ├─ clouds/         (3D density, generators)
                           ├─ physics/        (dust optical properties and phase law)
                           ├─ transport/      (ray traversal, direct, reverse)
                           └─ observables/    (sky directions, sample means/errors)
                                ↓
                         io/results.py + visualization/plots.py
                                ↓
                         outputs/... (gitignored)
```

## Contract for new modules

1. Cloud modules **only** create density fields; no plotting or random global state.
2. Physics modules define coefficients/scattering laws; no grid traversal.
3. Transport modules consume cloud and physics objects to estimate a **well-defined
   observable**; their input random state is a `numpy.random.Generator`.
4. Observable modules define direction bins, map arrays, aggregation, and errors.
5. Simulation wires components together; I/O and plotting live in separate modules.
6. The CLI is a thin adapter. New physics must not be implemented there.

For an issue that changes physics, include the equation, assumptions, units,
reference, limiting cases, and a test. For performance changes, establish
numerical equivalence before benchmarking speed.

## Caution: estimator bias and uncertainty

Never cut off a Monte Carlo path and treat it as an escaped path. The reverse
solver raises on `max_events` instead of silently biasing a result. A future
Russian-roulette termination policy must compensate surviving weights to
preserve unbiasedness.

The reported `stderr` is the naive independent-packet standard error for each
fixed sky direction. It does not include discretization/grid resolution error,
model parameter uncertainty, or finite angular quadrature error. Increasing
packets alone will not address those errors.

## Group-friendly extension points

- Add a Mathis cloud generator behind a `DensityGrid` return type.
- Add physically calibrated wavelength-dependent `OpticalProperties` without
  changing the ray traversal interface.
- Add an independent forward estimator with a specified detector/tally.
- Add a `BoundaryField` protocol if anisotropic external illumination is needed.
- Add a `SkySequence` module for camera-path fly-throughs.
- Keep gamma ray energy transport in its **own** physics + transport modules.
