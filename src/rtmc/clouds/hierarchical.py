"""Planned hierarchical cloud generator from Mathis et al. (2002), section 2."""

from rtmc.clouds.grid import DensityGrid


def mathis_hierarchical_cloud(
    resolution: int = 64,
    fractal_dimension: float = 2.6,
    seed: int = 2026,
    background_mass_fraction: float = 0.0,
) -> DensityGrid:
    """TODO: Implement the paper's four-level point casting and periodic wrapping.

    See docs/roadmap.md. Do not silently substitute Gaussian clumps: the
    density statistics and viewing-angle dependence are research outputs.
    """
    raise NotImplementedError(
        "Implement the 4-generation, 32-child hierarchical cloud model "
        "from Mathis et al. (2002), section 2, with tests."
    )
