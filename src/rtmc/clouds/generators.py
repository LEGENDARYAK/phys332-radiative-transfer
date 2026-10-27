"""Simple cloud generators; not a replacement for Mathis et al. section 2."""

import numpy as np

from rtmc.clouds.grid import DensityGrid


def uniform_cloud(resolution: int, radius: float = 1.0, mean_density: float = 1.0) -> DensityGrid:
    """A spherical, uniform-density cloud on a Cartesian grid."""
    if mean_density <= 0 or not np.isfinite(mean_density):
        raise ValueError("mean_density must be positive and finite")
    return DensityGrid(np.full((resolution,) * 3, mean_density), radius=radius)


def gaussian_clump_cloud(
    resolution: int,
    radius: float = 1.0,
    mean_density: float = 1.0,
    clump_strength: float = 0.9,
    n_clumps: int = 12,
    clump_width: float = 0.18,
    seed: int = 2026,
) -> DensityGrid:
    """Generate reproducible Gaussian clumps and normalize the in-sphere mean.

    This is a *toy structured cloud*, not the hierarchical/fractal recipe
    from Mathis, Whitney & Wood (2002). `clump_strength` blends uniform
    density (0) with normalized Gaussian clumps (1); it is NOT the ratio
    of maximum to minimum density.
    """
    if not 0 <= clump_strength <= 1:
        raise ValueError("clump_strength must be in [0, 1]")
    if n_clumps < 1 or clump_width <= 0:
        raise ValueError("n_clumps >= 1 and clump_width > 0 are required")
    if mean_density <= 0 or not np.isfinite(mean_density):
        raise ValueError("mean_density must be positive and finite")
    if resolution < 2 or radius <= 0:
        raise ValueError("resolution >= 2 and radius > 0 are required")

    coords = -radius + (np.arange(resolution) + 0.5) * (2 * radius / resolution)
    x, y, z = np.meshgrid(coords, coords, coords, indexing="ij")
    sphere = x * x + y * y + z * z <= radius * radius

    rng = np.random.default_rng(seed)
    lumps = np.zeros((resolution,) * 3, dtype=np.float64)
    width = clump_width * radius
    for _ in range(n_clumps):
        center = rng.uniform(-0.8 * radius, 0.8 * radius, size=3)
        amplitude = rng.lognormal(mean=0.0, sigma=0.7)
        d2 = (x - center[0]) ** 2 + (y - center[1]) ** 2 + (z - center[2]) ** 2
        lumps += amplitude * np.exp(-d2 / (2 * width**2))

    lumps += 0.001  # strictly positive between dense clumps
    lumps /= lumps[sphere].mean()
    density = mean_density * ((1 - clump_strength) + clump_strength * lumps)
    return DensityGrid(density, radius=radius)
