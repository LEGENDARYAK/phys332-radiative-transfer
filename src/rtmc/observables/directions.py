"""Equal-solid-angle bins for a complete sphere of look directions."""

import numpy as np
from numpy.typing import NDArray


def sky_directions(n_mu: int, n_phi: int) -> tuple[NDArray[np.float64], ...]:
    """Return (mu, phi, directions) with directions.shape=(n_mu,n_phi,3).

    Here mu=cos(theta) spans [-1,1] in uniform steps, phi spans [0,2pi).
    These cells have equal solid angle: dOmega=dphi*dmu. Thus the simple
    arithmetic mean of map pixels approximates the full-sky mean intensity.
    """
    if n_mu < 1 or n_phi < 1:
        raise ValueError("n_mu and n_phi must be positive")
    mu = -1.0 + (np.arange(n_mu) + 0.5) * (2.0 / n_mu)
    phi = (np.arange(n_phi) + 0.5) * (2.0 * np.pi / n_phi)
    mu_grid, phi_grid = np.meshgrid(mu, phi, indexing="ij")
    transverse = np.sqrt(1.0 - mu_grid**2)
    directions = np.stack(
        [transverse * np.cos(phi_grid), transverse * np.sin(phi_grid), mu_grid], axis=-1
    )
    return mu, phi, directions
