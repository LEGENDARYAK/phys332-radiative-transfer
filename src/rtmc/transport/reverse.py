"""Basic reverse Monte Carlo for a grey, reciprocal elastic scattering medium.

This directly illustrates Appendix A of Bethell et al. (2004), but is NOT
an inelastic gamma-ray adjoint solver and has not been validated against
Bethell's exact numerical benchmarks. Validate before scientific reporting.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from rtmc.clouds.grid import DensityGrid
from rtmc.physics.optics import OpticalProperties
from rtmc.physics.phase import sample_hg_direction
from rtmc.transport.direct import Estimate
from rtmc.transport.raytrace import normalize, trace_mass_column


@dataclass(frozen=True)
class ReverseScatteringSolver:
    """Trace paths backward from observer to isotropically lit boundary.

    Scattering is sampled using `kappa_scat * rho`; each ray's surviving
    weight is exp(-integral(kappa_abs * rho ds)). Every sample ends at the
    boundary. An excessive number of events raises rather than silently
    truncating a path and biasing the estimator.
    """

    cloud: DensityGrid
    optics: OpticalProperties
    background_intensity: float = 1.0
    max_events: int = 10_000

    def intensity(
        self,
        position: NDArray[np.float64],
        look_direction: NDArray[np.float64],
        rng: np.random.Generator | None = None,
        packets: int = 64,
    ) -> Estimate:
        if packets <= 0 or self.max_events <= 0:
            raise ValueError("packets and max_events must be positive")
        if rng is None:
            raise ValueError("Pass an explicit seeded numpy Generator for reproducibility")
        if self.optics.kappa_scat == 0:
            # Reverse without any scattering must equal direct pure absorption.
            column = trace_mass_column(self.cloud, position, look_direction).mass_column
            return Estimate(
                intensity=float(
                    self.background_intensity * np.exp(-self.optics.kappa_abs * column)
                ),
                stderr=0.0,
            )

        observations = np.empty(packets, dtype=np.float64)
        for i in range(packets):
            pos = np.asarray(position, dtype=np.float64).copy()
            ray_dir = normalize(look_direction)
            absorption_depth = 0.0
            for _ in range(self.max_events):
                tau_scattering = -np.log(1.0 - rng.random())
                target_column = tau_scattering / self.optics.kappa_scat
                segment = trace_mass_column(self.cloud, pos, ray_dir, target_column)
                absorption_depth += self.optics.kappa_abs * segment.mass_column
                if not segment.hit_target:
                    # The external boundary intensity is isotropic and = I0.
                    observations[i] = self.background_intensity * np.exp(-absorption_depth)
                    break
                pos = segment.position
                ray_dir = sample_hg_direction(ray_dir, self.optics.g, rng)
            else:
                raise RuntimeError(
                    f"Path exceeded {self.max_events} scattering events; "
                    "consider a larger limit or a correctly weighted Russian roulette."
                )
        return Estimate(
            intensity=float(observations.mean()),
            stderr=float(observations.std(ddof=1) / np.sqrt(packets)) if packets > 1 else 0.0,
        )
