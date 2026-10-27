"""Opacity and phase function tests."""

import numpy as np
import pytest

from rtmc.physics.optics import OpticalProperties
from rtmc.physics.phase import hg_cos_theta, sample_hg_direction


def test_optics_albedo() -> None:
    optics = OpticalProperties(0.4, 0.6, g=0.5)
    assert optics.kappa_ext == pytest.approx(1.0)
    assert optics.albedo == pytest.approx(0.6)


@pytest.mark.parametrize("g", [0.0, 0.5, -0.5])
def test_hg_mean_cosine(g: float) -> None:
    rng = np.random.default_rng(2026)
    values = [hg_cos_theta(g, float(u)) for u in rng.random(6_000)]
    assert np.mean(values) == pytest.approx(g, abs=0.03)


def test_scattered_directions_are_unit_vectors() -> None:
    rng = np.random.default_rng(12)
    for incoming in (np.array([0.0, 0.0, 1.0]), np.array([1.0, 2.0, -1.0])):
        for _ in range(30):
            out = sample_hg_direction(incoming, 0.6, rng)
            assert np.linalg.norm(out) == pytest.approx(1.0, abs=1e-12)


def test_optics_reject_invalid() -> None:
    with pytest.raises(ValueError):
        OpticalProperties(-1.0, 0.0)
    with pytest.raises(ValueError):
        OpticalProperties(1.0, 0.0, g=1.0)
