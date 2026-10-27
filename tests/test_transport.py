"""Limiting cases for direct and reverse numerical transport."""

import numpy as np
import pytest

from rtmc.clouds import uniform_cloud
from rtmc.config import load_config
from rtmc.physics.optics import OpticalProperties
from rtmc.simulation import run_experiment
from rtmc.transport.direct import UncollidedSolver
from rtmc.transport.reverse import ReverseScatteringSolver


def test_center_pure_absorption_is_exact() -> None:
    cloud = uniform_cloud(16, radius=1.0, mean_density=1.0)
    direct = UncollidedSolver(cloud, OpticalProperties(1.0, 0.0))
    rng = np.random.default_rng(2026)
    for direction in ((1, 0, 0), (1, 1, 1), (0, 0, -1)):
        estimated = direct.intensity(np.zeros(3), np.array(direction), rng).intensity
        assert estimated == pytest.approx(np.exp(-1), rel=1e-12)


def test_off_center_direction_dependence() -> None:
    cloud = uniform_cloud(12)
    direct = UncollidedSolver(cloud, OpticalProperties(1.0, 0.0))
    p = np.array([0.5, 0, 0])
    bright = direct.intensity(p, np.array([1.0, 0.0, 0.0])).intensity
    dark = direct.intensity(p, np.array([-1.0, 0.0, 0.0])).intensity
    assert bright == pytest.approx(np.exp(-0.5))
    assert dark == pytest.approx(np.exp(-1.5))


def test_scattering_loss_in_direct_beam() -> None:
    cloud = uniform_cloud(8)
    direct = UncollidedSolver(cloud, OpticalProperties(0.3, 0.7))
    intensity = direct.intensity(np.zeros(3), np.array([0, 0, 1])).intensity
    assert intensity == pytest.approx(np.exp(-1))


def test_reverse_no_scattering_equals_direct() -> None:
    cloud = uniform_cloud(8)
    optics = OpticalProperties(0.6, 0)
    direct = UncollidedSolver(cloud, optics)
    reverse = ReverseScatteringSolver(cloud, optics)
    position = np.array([0.3, 0.1, 0.1])
    direction = np.array([1.0, 0.2, 0.3])
    d = direct.intensity(position, direction)
    r = reverse.intensity(position, direction, np.random.default_rng(4), packets=30)
    assert d.intensity == pytest.approx(r.intensity)
    assert r.stderr == 0


def test_isotropic_pure_scattering_keeps_intensity() -> None:
    cloud = uniform_cloud(10)
    reverse = ReverseScatteringSolver(cloud, OpticalProperties(0.0, 1.5, g=0.3))
    estimated = reverse.intensity(
        np.array([0.1, 0, 0]), np.array([1, 0, 0]), np.random.default_rng(8), packets=40
    )
    assert estimated.intensity == pytest.approx(1.0, abs=1e-12)
    assert estimated.stderr == 0.0


def test_reverse_sample_reproducible() -> None:
    cloud = uniform_cloud(10)
    solver = ReverseScatteringSolver(cloud, OpticalProperties(0.4, 0.5, g=0.4))
    args = (np.zeros(3), np.array([1.0, 0.0, 0.0]))
    a = solver.intensity(*args, np.random.default_rng(22), packets=40)
    b = solver.intensity(*args, np.random.default_rng(22), packets=40)
    assert a == b
    assert 0 <= a.intensity <= 1
    assert a.stderr >= 0


def test_baseline_config_map() -> None:
    config = load_config("configs/baseline.toml")
    result = run_experiment(config)
    assert result.sky.intensity.shape == (16, 32)
    assert result.sky.mean_intensity == pytest.approx(np.exp(-1), rel=1e-12)
    assert result.sky.mean_stderr == 0.0
