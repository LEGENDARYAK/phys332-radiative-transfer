"""Exact line integrals through piecewise-constant 3D density voxels.

All rays start inside the inscribed sphere. Use 3D DDA to visit each voxel
once. A trajectory is clipped at the spherical surface, not the cube faces.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from rtmc.clouds.grid import DensityGrid


@dataclass(frozen=True)
class RayResult:
    distance: float
    mass_column: float
    position: NDArray[np.float64]
    hit_target: bool


def normalize(direction: NDArray[np.float64] | tuple[float, ...]) -> NDArray[np.float64]:
    d = np.asarray(direction, dtype=np.float64)
    if d.shape != (3,) or not np.isfinite(d).all():
        raise ValueError("direction must be a finite 3-vector")
    norm = np.linalg.norm(d)
    if norm == 0:
        raise ValueError("direction must be nonzero")
    return d / norm


def distance_to_sphere_exit(
    position: NDArray[np.float64], direction: NDArray[np.float64], radius: float
) -> float:
    """Distance to next boundary intersection, from a position inside/on sphere."""
    p = np.asarray(position, dtype=np.float64)
    d = normalize(direction)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError("position must be a finite 3-vector")
    if np.linalg.norm(p) > radius * (1 + 1e-11):
        raise ValueError("Ray origin lies outside cloud sphere")
    b = float(p @ d)
    discriminant = max(0.0, b * b + radius * radius - float(p @ p))
    return max(0.0, -b + np.sqrt(discriminant))


def trace_mass_column(
    grid: DensityGrid,
    origin: NDArray[np.float64] | tuple[float, ...],
    direction: NDArray[np.float64] | tuple[float, ...],
    target_column: float | None = None,
) -> RayResult:
    """Integrate density ds until exiting sphere or reaching `target_column`.

    The target is useful for Monte Carlo: draw scattering optical depth,
    divide by kappa_scat, then find the next collision position. `mass_column`
    is the integral of density along the traversed ray. The origin is assumed
    to be in the sphere; the result position is on the sphere or at a collision.
    """
    p = np.asarray(origin, dtype=np.float64)
    d = normalize(direction)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError("origin must be a finite 3-vector")
    if target_column is not None and (not np.isfinite(target_column) or target_column < 0):
        raise ValueError("target_column must be finite and nonnegative")
    t_exit = distance_to_sphere_exit(p, d, grid.radius)
    if target_column == 0:
        return RayResult(distance=0.0, mass_column=0.0, position=p.copy(), hit_target=True)

    if t_exit == 0:
        return RayResult(distance=0.0, mass_column=0.0, position=p.copy(), hit_target=False)

    # Place a point lying exactly on a voxel face in the cell into which
    # the ray travels. This also handles rays beginning at x=+/-radius.
    scaled = (p + grid.radius) / grid.dx
    scaled = np.nextafter(scaled, scaled + np.where(d >= 0, 1.0, -1.0))
    idx = np.floor(scaled).astype(int)
    if np.any(idx < 0) or np.any(idx >= grid.resolution):
        raise RuntimeError("Failed to locate initial voxel; check cloud geometry")

    step = np.sign(d).astype(int)
    t_max = np.full(3, np.inf, dtype=float)
    t_delta = np.full(3, np.inf, dtype=float)
    for a in range(3):
        if step[a]:
            face = idx[a] + (1 if step[a] > 0 else 0)
            face_coordinate = -grid.radius + face * grid.dx
            t_max[a] = max(0.0, (face_coordinate - p[a]) / d[a])
            t_delta[a] = grid.dx / abs(d[a])

    t = 0.0
    column = 0.0
    # A straight ray cannot cross more than ~3n cell faces in a cubic grid.
    for _ in range(3 * grid.resolution + 6):
        next_face = float(np.min(t_max))
        t_next = min(t_exit, next_face)
        # Floating-point grid faces may lie ~1 ulp inside the exact sphere edge.
        if abs(t_exit - next_face) <= 2e-12 * max(1.0, t_exit):
            t_next = t_exit
        dt = max(0.0, t_next - t)
        density = float(grid.values[tuple(idx)])
        incremental_column = density * dt

        if target_column is not None and column + incremental_column >= target_column:
            distance = t + (target_column - column) / density
            return RayResult(
                distance=distance,
                mass_column=target_column,
                position=p + distance * d,
                hit_target=True,
            )

        column += incremental_column
        t = t_next
        if t >= t_exit:
            return RayResult(
                distance=t_exit,
                mass_column=column,
                position=p + t_exit * d,
                hit_target=False,
            )

        # Crossing a corner/edge requires advancing all tied coordinates.
        for a in range(3):
            if t_max[a] <= next_face + 1e-12 * max(1.0, abs(next_face)):
                idx[a] += step[a]
                t_max[a] += t_delta[a]
        if np.any(idx < 0) or np.any(idx >= grid.resolution):
            raise RuntimeError("Exited grid cube before spherical boundary")

    raise RuntimeError("Voxel traversal exceeded step limit")
