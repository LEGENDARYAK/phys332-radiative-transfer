"""Elastic Henyey-Greenstein scattering-angle sampling."""

import numpy as np
from numpy.typing import NDArray


def hg_cos_theta(g: float, u: float) -> float:
    """Inverse-CDF sample of cos(deflection angle), for u in [0, 1]."""
    if not -1 < g < 1 or not 0 <= u <= 1:
        raise ValueError("Expected -1 < g < 1 and 0 <= u <= 1")
    if abs(g) < 1e-8:
        return 2.0 * u - 1.0
    ratio = (1.0 - g * g) / (1.0 - g + 2.0 * g * u)
    return float(np.clip((1.0 + g * g - ratio * ratio) / (2.0 * g), -1.0, 1.0))


def sample_hg_direction(
    incoming: NDArray[np.float64], g: float, rng: np.random.Generator
) -> NDArray[np.float64]:
    """Deflect a unit ray direction with HG polar angle and uniform azimuth."""
    d = np.asarray(incoming, dtype=np.float64)
    norm = np.linalg.norm(d)
    if d.shape != (3,) or not np.isfinite(norm) or norm == 0:
        raise ValueError("incoming must be a finite, nonzero 3-vector")
    d = d / norm

    mu = hg_cos_theta(g, float(rng.random()))
    phi = 2.0 * np.pi * rng.random()
    helper = np.array([0.0, 0.0, 1.0] if abs(d[2]) < 0.9 else [0.0, 1.0, 0.0])
    e1 = np.cross(helper, d)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    transverse = np.sqrt(max(0.0, 1.0 - mu * mu))
    out = mu * d + transverse * (np.cos(phi) * e1 + np.sin(phi) * e2)
    return out / np.linalg.norm(out)
