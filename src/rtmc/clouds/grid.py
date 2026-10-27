"""Cloud density data structure and dimensional conventions."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class DensityGrid:
    """Density on a cubic Cartesian grid enclosing a spherical cloud.

    `values[i, j, k]` is density in arbitrary but consistent units.
    The cube spans [-radius, radius]^3; only points inside the inscribed
    sphere participate in transport. Values represent piecewise-constant
    density within each voxel. The sphere's center is the origin.
    """

    values: NDArray[np.float64]
    radius: float = 1.0

    def __post_init__(self) -> None:
        arr = np.asarray(self.values, dtype=np.float64)
        if arr.ndim != 3 or len(set(arr.shape)) != 1 or arr.shape[0] < 2:
            raise ValueError("DensityGrid requires a cubic (n, n, n) array with n >= 2")
        if not np.isfinite(arr).all() or np.any(arr < 0):
            raise ValueError("Densities must be finite and nonnegative")
        if not np.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("radius must be a positive, finite number")
        # A frozen dataclass does not prevent mutating an array; take an immutable copy.
        arr = arr.copy()
        arr.setflags(write=False)
        object.__setattr__(self, "values", arr)

    @property
    def resolution(self) -> int:
        return self.values.shape[0]

    @property
    def dx(self) -> float:
        return 2.0 * self.radius / self.resolution

    def axis_centers(self) -> NDArray[np.float64]:
        return -self.radius + (np.arange(self.resolution) + 0.5) * self.dx

    def contains(self, position: NDArray[np.float64] | tuple[float, ...]) -> bool:
        point = np.asarray(position, dtype=np.float64)
        return bool(point.shape == (3,) and np.linalg.norm(point) <= self.radius + 1e-12)
