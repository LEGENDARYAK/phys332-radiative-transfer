"""TOML experiment config, with explicit defaults and validation."""

import tomllib
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path
from typing import Any

from rtmc.physics.optics import OpticalProperties


@dataclass(frozen=True)
class CloudConfig:
    kind: str = "uniform"
    resolution: int = 32
    radius: float = 1.0
    mean_density: float = 1.0
    clump_strength: float = 0.9
    n_clumps: int = 12
    clump_width: float = 0.18
    seed: int = 2026

    def __post_init__(self) -> None:
        if self.kind not in {"uniform", "gaussian_clumps"}:
            raise ValueError("cloud.kind must be uniform or gaussian_clumps")
        if not isinstance(self.resolution, int) or self.resolution < 2:
            raise ValueError("cloud.resolution must be an integer >= 2")
        if not all(isfinite(x) and x > 0 for x in (self.radius, self.mean_density)):
            raise ValueError("cloud radius and mean density must be positive and finite")
        if not 0 <= self.clump_strength <= 1:
            raise ValueError("cloud.clump_strength must be in [0, 1]")
        if not isinstance(self.n_clumps, int) or self.n_clumps < 1:
            raise ValueError("cloud.n_clumps must be a positive integer")
        if not isfinite(self.clump_width) or self.clump_width <= 0:
            raise ValueError("cloud.clump_width must be finite and positive")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("cloud.seed must be a nonnegative integer")


@dataclass(frozen=True)
class OpticsConfig:
    kappa_abs: float = 1.0
    kappa_scat: float = 0.0
    g: float = 0.0

    def __post_init__(self) -> None:
        OpticalProperties(self.kappa_abs, self.kappa_scat, self.g)


@dataclass(frozen=True)
class BackgroundConfig:
    intensity: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.intensity) or self.intensity < 0:
            raise ValueError("background.intensity must be finite and >= 0")


@dataclass(frozen=True)
class ObserverConfig:
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        if len(self.position) != 3 or not all(isfinite(x) for x in self.position):
            raise ValueError("observer.position must contain three finite coordinates")


@dataclass(frozen=True)
class SimulationConfig:
    solver: str = "uncollided"
    mu_bins: int = 12
    phi_bins: int = 24
    packets_per_direction: int = 32
    seed: int = 2026
    max_events: int = 10_000

    def __post_init__(self) -> None:
        if self.solver not in {"uncollided", "reverse"}:
            raise ValueError("simulation.solver must be uncollided or reverse")
        for name in ("mu_bins", "phi_bins", "packets_per_direction", "max_events"):
            v = getattr(self, name)
            if not isinstance(v, int) or v <= 0:
                raise ValueError(f"simulation.{name} must be a positive integer")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("simulation.seed must be a nonnegative integer")


@dataclass(frozen=True)
class ExperimentConfig:
    cloud: CloudConfig
    optics: OpticsConfig
    background: BackgroundConfig
    observer: ObserverConfig
    simulation: SimulationConfig

    def __post_init__(self) -> None:
        radius_squared = self.cloud.radius * self.cloud.radius
        position_squared = sum(coord * coord for coord in self.observer.position)
        if position_squared > radius_squared * (1 + 1e-11):
            raise ValueError("observer.position must lie within the spherical cloud")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> ExperimentConfig:
    config_path = Path(path)
    with config_path.open("rb") as f:
        data = tomllib.load(f)
    unexpected = set(data) - {"cloud", "optics", "background", "observer", "simulation"}
    if unexpected:
        raise ValueError(f"Unknown configuration sections: {', '.join(sorted(unexpected))}")
    try:
        observer_data = data.get("observer", {}).copy()
        if "position" in observer_data:
            observer_data["position"] = tuple(observer_data["position"])
        config = ExperimentConfig(
            cloud=CloudConfig(**data.get("cloud", {})),
            optics=OpticsConfig(**data.get("optics", {})),
            background=BackgroundConfig(**data.get("background", {})),
            observer=ObserverConfig(**observer_data),
            simulation=SimulationConfig(**data.get("simulation", {})),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid configuration in {config_path}: {exc}") from exc
    # The configs are validated when their dataclasses are instantiated.
    return config
