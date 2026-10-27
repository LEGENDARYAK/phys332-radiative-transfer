"""Wires config to cloud, physics, solver, and observable; no plotting or I/O."""

from dataclasses import dataclass

import numpy as np

from rtmc.clouds.generators import gaussian_clump_cloud, uniform_cloud
from rtmc.clouds.grid import DensityGrid
from rtmc.config import ExperimentConfig
from rtmc.observables.sky import SkyMap, compute_sky_map
from rtmc.physics.optics import OpticalProperties
from rtmc.transport.direct import UncollidedSolver
from rtmc.transport.reverse import ReverseScatteringSolver


@dataclass(frozen=True)
class ExperimentResult:
    cloud: DensityGrid
    sky: SkyMap
    optics: OpticalProperties


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    c = config.cloud
    if c.kind == "uniform":
        cloud = uniform_cloud(c.resolution, c.radius, c.mean_density)
    elif c.kind == "gaussian_clumps":
        cloud = gaussian_clump_cloud(
            c.resolution,
            c.radius,
            c.mean_density,
            c.clump_strength,
            c.n_clumps,
            c.clump_width,
            c.seed,
        )
    else:
        raise ValueError(f"Unknown cloud kind: {c.kind}")

    optics = OpticalProperties(
        config.optics.kappa_abs, config.optics.kappa_scat, config.optics.g
    )
    position = np.asarray(config.observer.position, dtype=np.float64)
    if not cloud.contains(position):
        raise ValueError("Observer must be located within the spherical cloud")

    if config.simulation.solver == "uncollided":
        solver = UncollidedSolver(cloud, optics, config.background.intensity)
    elif config.simulation.solver == "reverse":
        solver = ReverseScatteringSolver(
            cloud, optics, config.background.intensity, config.simulation.max_events
        )
    else:
        raise ValueError(f"Unknown solver: {config.simulation.solver}")

    rng = np.random.default_rng(config.simulation.seed)
    sky = compute_sky_map(
        solver,
        position,
        config.simulation.mu_bins,
        config.simulation.phi_bins,
        config.simulation.packets_per_direction,
        rng,
    )
    return ExperimentResult(cloud=cloud, sky=sky, optics=optics)
