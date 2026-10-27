"""Checks for density shape, normalization, and reproducible generators."""

import numpy as np
import pytest

from rtmc.clouds import DensityGrid, gaussian_clump_cloud, uniform_cloud


def test_uniform_grid_and_mean() -> None:
    cloud = uniform_cloud(resolution=12, radius=2.0, mean_density=3.0)
    assert cloud.values.shape == (12, 12, 12)
    assert cloud.dx == pytest.approx(4.0 / 12)
    assert cloud.values.mean() == pytest.approx(3.0)


def test_clumpy_seed_reproducibility_and_mean() -> None:
    a = gaussian_clump_cloud(resolution=20, seed=5)
    b = gaussian_clump_cloud(resolution=20, seed=5)
    c = gaussian_clump_cloud(resolution=20, seed=6)
    assert np.array_equal(a.values, b.values)
    assert not np.array_equal(a.values, c.values)
    coords = a.axis_centers()
    x, y, z = np.meshgrid(coords, coords, coords, indexing="ij")
    inside = x * x + y * y + z * z <= a.radius**2
    assert a.values[inside].mean() == pytest.approx(1.0)
    assert a.values[inside].std() > 0


def test_cloud_values_not_mutable() -> None:
    cloud = uniform_cloud(4)
    with pytest.raises(ValueError):
        cloud.values[0, 0, 0] = 5


def test_density_validation() -> None:
    with pytest.raises(ValueError):
        DensityGrid(np.ones((3, 3, 4)))
    with pytest.raises(ValueError):
        DensityGrid(-np.ones((3, 3, 3)))
