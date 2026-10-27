"""Direction-resolved radiation and angular averages at an observer."""

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from rtmc.observables.directions import sky_directions
from rtmc.transport.direct import Estimate


class DirectionalSolver(Protocol):
    def intensity(
        self,
        position: NDArray[np.float64],
        look_direction: NDArray[np.float64],
        rng: np.random.Generator | None = None,
        packets: int = 1,
    ) -> Estimate: ...


@dataclass(frozen=True)
class SkyMap:
    mu: NDArray[np.float64]
    phi: NDArray[np.float64]
    intensity: NDArray[np.float64]
    stderr: NDArray[np.float64]

    @property
    def mean_intensity(self) -> float:
        """J = (1 / 4pi) integral I dOmega (equal-solid-angle midpoint rule)."""
        return float(self.intensity.mean())

    @property
    def mean_stderr(self) -> float:
        """Uncertainty of J, assuming independent packet streams per pixel."""
        return float(np.sqrt(np.sum(self.stderr**2)) / self.stderr.size)


def compute_sky_map(
    solver: DirectionalSolver,
    position: NDArray[np.float64],
    n_mu: int,
    n_phi: int,
    packets: int,
    rng: np.random.Generator,
) -> SkyMap:
    mu, phi, directions = sky_directions(n_mu, n_phi)
    intensity = np.empty((n_mu, n_phi), dtype=float)
    stderr = np.empty_like(intensity)
    for i in range(n_mu):
        for j in range(n_phi):
            est = solver.intensity(position, directions[i, j], rng=rng, packets=packets)
            intensity[i, j] = est.intensity
            stderr[i, j] = est.stderr
    return SkyMap(mu=mu, phi=phi, intensity=intensity, stderr=stderr)
