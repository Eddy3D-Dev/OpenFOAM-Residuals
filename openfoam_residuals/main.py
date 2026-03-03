"""
Parse and plot OpenFOAM residual files.

Examples
--------
# One explicit file
python main.py -f /path/to/residuals/U_residuals.dat -o out

# One case directory (auto-find residual files)
python main.py -w ~/cases/cavity

# Multiple cases, verbose, skip PNGs
python main.py -w case1 -w case2 -vv --no-plots
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from openfoam_residuals import filesystem as fs
from openfoam_residuals import plot as pl

if TYPE_CHECKING:
    from collections.abc import Iterable

_LOG = logging.getLogger(__name__)


# ───────────────────────────── CLI parsing ──────────────────────────────
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the residual plotting CLI."""
    parser = argparse.ArgumentParser(
        description="Locate OpenFOAM residual files, "
        "compute min/max iterations and export plots/data.",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # mutually-exclusive group: either a single file OR one/more work dirs
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        help="Path to a single residual*.dat file to plot/export.",
    )
    group.add_argument(
        "-w",
        "--work-dir",
        action="append",
        metavar="DIR",
        help="Case directory that contains residual*.dat files "
        "(may be given multiple times).",
    )

    parser.add_argument(
        "-o",
        "--out",
        default="exports",
        metavar="DIR",
        help="Output directory for exported CSV/PNGs (default: %(default)s)",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Export data files only (skip PNG generation).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (-v, -vv).",
    )
    return parser.parse_args()


# ───────────────────────────── helpers ──────────────────────────────────
def configure_logging(verbosity: int) -> None:
    """Configure logging level based on verbosity."""
    level = logging.WARNING - min(verbosity, 2) * 10
    logging.basicConfig(level=level, format="%(levelname)s │ %(message)s")


def gather_from_dirs(dirs: Iterable[str | Path]) -> list[Path]:
    """Find all residual files in the provided directories."""
    residual_files: list[Path] = []
    for work_dir in map(Path, dirs):
        if not work_dir.exists():
            _LOG.error("Work dir %s does not exist -- skipping.", work_dir)
            continue
        files = fs.find_residual_files(work_dir)
        if not files:
            _LOG.warning("No residual files found in %s", work_dir)
        residual_files.extend(files)
    return residual_files


# ───────────────────────────── main routine ─────────────────────────────
def main() -> None:
    """Parse, compute, and export residual plots."""
    args = parse_args()
    configure_logging(args.verbose)

    # Resolve input(s)
    if args.file:
        residual_files = [Path(args.file).resolve()]
        if not residual_files[0].exists():
            _LOG.error(
                "File '%s' not found.\n"
                "       Hint: Check that the path is correct and the file exists.",
                residual_files[0],
            )
            sys.exit(1)
        _LOG.info("Using single file: %s", residual_files[0])
    else:
        residual_files = gather_from_dirs(args.work_dir)
        if not residual_files:
            _LOG.error(
                "No residual files found in supplied directories.\n"
                "       Hint: Ensure the directories contain files matching 'residuals*.dat'."
            )
            sys.exit(1)

    # Compute min/max iteration over the chosen set
    min_val, max_iter = fs.find_min_and_max_iteration(residual_files)
    _LOG.info("Global min residual: %g   max iteration: %d", min_val, max_iter)

    # Prepare output folder
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    _LOG.debug("Export directory: %s", out_dir)

    # Export
    if not args.no_plots:
        print(f"Processing {len(residual_files)} residual file(s)...")
        pl.export_files(
            residual_files,
            min_val,
            max_iter,
            output_dir=out_dir,
        )
        print(f"✨ Successfully exported {len(residual_files)} plot(s) to {out_dir}")
    else:
        _LOG.info("Skipping plot generation (--no-plots).")

    _LOG.info("Done - results in %s", out_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _LOG.warning("Interrupted by user - aborting.")
        sys.exit(130)
    except fs.DataParseError as e:
        _LOG.error(str(e))
        sys.exit(1)
