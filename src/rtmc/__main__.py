"""Allow `python -m rtmc ...` as well as the `rtmc ...` console script."""

from rtmc.cli import main

raise SystemExit(main())
