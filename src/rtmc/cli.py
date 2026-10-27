"""`rtmc` command: a stable entry point for group experiments."""

import argparse
from pathlib import Path

from rtmc.config import load_config
from rtmc.io.results import save_result
from rtmc.simulation import run_experiment
from rtmc.visualization.plots import plot_density_slice, plot_sky_map


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PHYS 332 Monte Carlo radiative transfer")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="Run and save a simulation")
    run.add_argument("--config", "-c", type=Path, required=True)
    run.add_argument("--output", "-o", type=Path, default=Path("outputs/latest"))

    check = commands.add_parser("check-config", help="Validate configuration")
    check.add_argument("--config", "-c", type=Path, required=True)

    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "check-config":
            print(f"Configuration OK: {args.config}")
            return 0
        result = run_experiment(config)
        output = save_result(result, config, args.output)
        plot_sky_map(result.sky, output / "sky_map.png")
        plot_density_slice(result.cloud, output / "density_slice.png")
        print(f"Results: {output.resolve()}")
        print(f"Mean sky intensity J: {result.sky.mean_intensity:.6g}")
        print(f"Estimated standard error of J: {result.sky.mean_stderr:.3g}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
