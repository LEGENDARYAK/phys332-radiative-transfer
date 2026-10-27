"""Analytic direct/uncollided ray estimator, useful as a baseline."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from rtmc.clouds.grid import DensityGrid
from rtmc.physics.optics import OpticalProperties
from rtmc.transport.raytrace import trace_mass_column


@dataclass(frozen=True)
class Estimate:
    intensity: float
    stderr: float


@dataclass(frozen=True)
class UncollidedSolver:
    """Predicts only photons that have not scattered or been absorbed.

    If scattering opacity is zero, this is the *complete* pure-absorption
    solution. If scattering opacity is positive, scattered-in contributions
    are omitted: use ReverseScatteringSolver for the full radiation field.
    """

    cloud: DensityGrid
    optics: OpticalProperties
    background_intensity: float = 1.0

    def intensity(
        self,
        position: NDArray[np.float64],
        look_direction: NDArray[np.float64],
        rng: np.random.Generator | None = None,
        packets: int = 1,
    ) -> Estimate:
        del rng, packets  # deterministic estimator, same interface as reverse solver
        column = trace_mass_column(self.cloud, position, look_direction).mass_column
        intensity = self.background_intensity * np.exp(-self.optics.kappa_ext * column)
        return Estimate(intensity=float(intensity), stderr=0.0)
