"""Exact uniform-sphere and spatially varying voxel traversal checks."""

import numpy as np
import pytest

from rtmc.clouds import DensityGrid, uniform_cloud
from rtmc.transport.raytrace import (
    distance_to_sphere_exit,
    normalize,
    trace_mass_column,
)


@pytest.mark.parametrize(
    "direction", [(1.0, 0.0, 0.0), (0.0, 0.0, 3.0), (1.0, 2.0, 3.0)]
)
def test_uniform_from_center(direction: tuple[float, ...]) -> None:
    cloud = uniform_cloud(16, radius=2.0, mean_density=3.0)
    result = trace_mass_column(cloud, (0.0, 0.0, 0.0), direction)
    assert result.distance == pytest.approx(2.0, abs=1e-12)
    assert result.mass_column == pytest.approx(6.0, abs=1e-12)
    assert np.linalg.norm(result.position) == pytest.approx(2.0)
    assert not result.hit_target


def test_uniform_off_center_and_target() -> None:
    cloud = uniform_cloud(18, radius=1.0, mean_density=3.0)
    full = trace_mass_column(cloud, (0.3, 0.0, 0.0), (1.0, 0.0, 0.0))
    assert full.distance == pytest.approx(0.7)
    assert full.mass_column == pytest.approx(2.1)
    target = trace_mass_column(cloud, (0.3, 0, 0), (1, 0, 0), target_column=1.5)
    assert target.hit_target
    assert target.distance == pytest.approx(0.5)
    assert target.mass_column == pytest.approx(1.5)
    assert target.position[0] == pytest.approx(0.8)


def test_piecewise_constant_density() -> None:
    density = np.ones((4, 4, 4))
    density[3, 2, 2] = 3  # x in [0.5,1], y,z in [0,0.5]
    cloud = DensityGrid(density, radius=1.0)
    result = trace_mass_column(cloud, (0, 0, 0), (1, 0, 0))
    assert result.mass_column == pytest.approx(0.5 + 3 * 0.5)


def test_diagonal_against_fine_midpoint_quadrature() -> None:
    rng = np.random.default_rng(1)
    cloud = DensityGrid(rng.uniform(0.1, 3, size=(12, 12, 12)))
    p = np.array([0.2, -0.1, 0.05])
    d = normalize((1, 0.37, 0.23))
    exact = trace_mass_column(cloud, p, d).mass_column
    length = distance_to_sphere_exit(p, d, cloud.radius)
    n = 100_000
    t = (np.arange(n) + 0.5) * length / n
    xyz = p[None, :] + t[:, None] * d[None, :]
    idx = np.floor((xyz + cloud.radius) / cloud.dx).astype(int)
    approximate = cloud.values[idx[:, 0], idx[:, 1], idx[:, 2]].mean() * length
    assert exact == pytest.approx(approximate, abs=2e-4)


def test_reject_origin_outside() -> None:
    cloud = uniform_cloud(8)
    with pytest.raises(ValueError):
        trace_mass_column(cloud, (2, 0, 0), (1, 0, 0))
