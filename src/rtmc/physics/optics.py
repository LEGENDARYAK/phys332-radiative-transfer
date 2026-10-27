"""A grey (single wavelength), elastic-scattering dust model."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class OpticalProperties:
    """Opacity per density unit (units: 1 / [density] / [length]).

    Local absorption/scattering coefficients are `density * kappa_*`.
    `g` is the Henyey-Greenstein asymmetry parameter. This model has no
    frequency changes, thermal re-emission, or gamma-ray interactions.
    """

    kappa_abs: float
    kappa_scat: float
    g: float = 0.0

    def __post_init__(self) -> None:
        if not all(isfinite(x) for x in (self.kappa_abs, self.kappa_scat, self.g)):
            raise ValueError("Optical parameters must be finite")
        if self.kappa_abs < 0 or self.kappa_scat < 0:
            raise ValueError("Opacity coefficients must be nonnegative")
        if not -1 < self.g < 1:
            raise ValueError("HG asymmetry g must be strictly between -1 and 1")

    @property
    def kappa_ext(self) -> float:
        return self.kappa_abs + self.kappa_scat

    @property
    def albedo(self) -> float:
        return self.kappa_scat / self.kappa_ext if self.kappa_ext else 0.0
