"""Smoke tests for shared experiment configuration and saved outputs."""

import json
from pathlib import Path

import numpy as np
import pytest

from rtmc.cli import main
from rtmc.config import load_config
from rtmc.observables.directions import sky_directions


def test_equal_solid_angle_directions_are_unit_vectors() -> None:
    mu, phi, dirs = sky_directions(20, 40)
    assert mu.shape == (20,)
    assert phi.shape == (40,)
    assert dirs.shape == (20, 40, 3)
    assert np.allclose(np.linalg.norm(dirs, axis=-1), 1.0)
    assert mu.mean() == pytest.approx(0)


def test_cli_run_writes_all_outputs(tmp_path: Path) -> None:
    out = tmp_path / "simulation"
    assert main(["run", "-c", "configs/baseline.toml", "-o", str(out)]) == 0
    assert (out / "sky_map.npz").is_file()
    assert (out / "sky_map.png").is_file()
    assert (out / "density_slice.png").is_file()
    with np.load(out / "sky_map.npz") as data:
        assert data["intensity"].shape == (16, 32)
    metadata = json.loads((out / "metadata.json").read_text())
    assert metadata["config"]["simulation"]["seed"] == 2026


def test_config_rejects_unknown_section(tmp_path: Path) -> None:
    config = tmp_path / "bad.toml"
    config.write_text("[wrong_section]\nhello = true\n")
    with pytest.raises(ValueError, match="Unknown configuration sections"):
        load_config(config)


def test_clumpy_example_loads() -> None:
    config = load_config("configs/clumpy_reverse.toml")
    assert config.simulation.solver == "reverse"
    assert config.cloud.kind == "gaussian_clumps"


def test_config_rejects_negative_opacity(tmp_path: Path) -> None:
    config = tmp_path / "bad_opacity.toml"
    config.write_text("[optics]\nkappa_abs = -1.0\n")
    with pytest.raises(ValueError, match="nonnegative"):
        load_config(config)


def test_config_rejects_outside_observer(tmp_path: Path) -> None:
    config = tmp_path / "outside.toml"
    config.write_text("[observer]\nposition = [3.0, 0.0, 0.0]\n")
    with pytest.raises(ValueError, match="within the spherical cloud"):
        load_config(config)
