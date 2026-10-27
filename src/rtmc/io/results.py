"""Store numerical results separately from plotting and physics."""

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from rtmc import __version__
from rtmc.config import ExperimentConfig
from rtmc.simulation import ExperimentResult


def save_result(
    result: ExperimentResult, config: ExperimentConfig, output_dir: str | Path
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_dir / "sky_map.npz",
        mu=result.sky.mu,
        phi=result.sky.phi,
        intensity=result.sky.intensity,
        stderr=result.sky.stderr,
    )
    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rtmc_version": __version__,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "config": config.to_dict(),
        "observables": {
            "mean_intensity": result.sky.mean_intensity,
            "mean_intensity_stderr": result.sky.mean_stderr,
            "albedo": result.optics.albedo,
        },
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return output_dir
