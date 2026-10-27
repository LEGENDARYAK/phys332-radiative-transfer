"""Publication-friendly, headless PNG plots for results and cloud slices."""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from rtmc.clouds.grid import DensityGrid
from rtmc.observables.sky import SkyMap


def plot_sky_map(sky: SkyMap, destination: str | Path) -> None:
    """Equirectangular map: azimuth (deg) vs latitude (deg)."""
    fig = Figure(figsize=(9, 4.7), layout="constrained")
    ax = fig.subplots()
    img = ax.imshow(
        sky.intensity,
        origin="lower",
        aspect="auto",
        extent=(0, 360, -90, 90),
        interpolation="nearest",
    )
    ax.set_title("Radiation sky map at observer")
    ax.set_xlabel("Azimuth (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    fig.colorbar(img, ax=ax, label="Specific intensity (input units)")
    fig.savefig(destination, dpi=150)


def plot_density_slice(cloud: DensityGrid, destination: str | Path) -> None:
    """Middle z-slice, with data outside sphere masked for visualization."""
    z = cloud.resolution // 2
    centers = cloud.axis_centers()
    x, y = np.meshgrid(centers, centers, indexing="ij")
    z_coord = centers[z]
    mask = x * x + y * y + z_coord * z_coord <= cloud.radius**2
    slice_data = np.where(mask, cloud.values[:, :, z], np.nan)
    fig = Figure(figsize=(5.8, 5.2), layout="constrained")
    ax = fig.subplots()
    im = ax.imshow(
        slice_data.T,
        origin="lower",
        extent=(-cloud.radius, cloud.radius, -cloud.radius, cloud.radius),
        interpolation="nearest",
    )
    ax.set_title("Cloud density (central z-slice)")
    ax.set_xlabel("x (simulation length units)")
    ax.set_ylabel("y (simulation length units)")
    fig.colorbar(im, ax=ax, label="Density (simulation units)")
    fig.savefig(destination, dpi=150)
