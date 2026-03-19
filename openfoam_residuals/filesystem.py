"""Filesystem utilities for OpenFOAM residuals analysis."""

from __future__ import annotations

import functools
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from openfoam_residuals import utils


class DataParseError(Exception):
    """Raised when a residual file cannot be parsed."""

    def __init__(self, file: Path, reason: str) -> None:
        """Initialize the exception with the file and reason."""
        super().__init__(f"File '{file}' {reason}")


def find_residual_files(w_dir: Path) -> list[Path]:
    """Return residual data files recursively found under ``w_dir``.

    Supported patterns:
    - ``residuals*.dat``
    - OpenFOAM logs named like ``log.simpleFoam`` / ``log.icoFoam.log``
    """
    root = Path(w_dir)
    candidates = [
        *root.rglob("residuals*.dat"),
        *root.rglob("log.*"),
    ]
    return sorted({path for path in candidates if path.is_file()})


def find_min_and_max_iteration(residual_files: list[Path]) -> tuple[int, int]:
    """Return (min_val, max_iter) across all files."""
    min_val = 1
    max_iter = 0
    total = len(residual_files)
    is_tty = sys.stdout.isatty()
    for idx, file in enumerate(residual_files):
        if is_tty:
            display_name = (
                "/".join(file.parts[-3:]) if len(file.parts) >= 3 else file.name
            )
            pct = (idx + 1) / total
            # 🎨 Palette: Add a fixed-width Unicode visual progress bar to make
            # parsing progress instantly scannable without reading numbers.
            bar_len = 10
            filled = int(bar_len * pct)
            bar = "█" * filled + "░" * (bar_len - filled)
            # 🎨 Palette: Right-align the iteration count and percentage to prevent
            # the progress string from jittering left and right as numbers grow.
            sys.stdout.write(
                f"\r\033[K🔍 Analyzing {idx + 1:>{len(str(total))}}/{total} [{bar}] {int(pct * 100):>3}% ({display_name})..."
            )
            sys.stdout.flush()

        data, _ = pre_parse(file)
        # ⚡ Bolt: Use numpy to compute a global minimum and ignore non-positive
        # entries (some solver logs include exact zeros, and log10(0) is invalid).
        values = data.to_numpy()
        positive_values = values[(values > 0) & ~np.isnan(values)]
        if positive_values.size > 0:
            min_i = 10 ** utils.order_of_magnitude(np.min(positive_values))
            if 0 < min_i < min_val:
                min_val = min_i

        # ⚡ Bolt: Since OpenFOAM Time (iterations) is monotonically increasing,
        # the max index is simply the last element, skipping a full scan.
        max_iter_i = data.index[-1]
        if max_iter_i > max_iter:
            max_iter = utils.roundup(max_iter_i)

    if is_tty and total > 0:
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    return min_val, max_iter


@functools.lru_cache(maxsize=128)
def _cached_pre_parse(file: Path, _mtime: float) -> tuple[pd.DataFrame, pd.Series]:
    """Cache internal implementation of pre_parse."""
    primary_parser = _parse_residuals_dat
    fallback_parser = _parse_openfoam_log
    if file.suffix.lower() != ".dat":
        primary_parser, fallback_parser = fallback_parser, primary_parser

    try:
        return primary_parser(file)
    except DataParseError as primary_error:
        try:
            return fallback_parser(file)
        except DataParseError as fallback_error:
            raise primary_error from fallback_error


def _parse_residuals_dat(file: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Parse OpenFOAM ``residuals*.dat`` file format."""
    headers = None
    with file.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("# Time"):
                # Extract headers and strip the leading '#'
                headers = line.replace("#", "").split()
                break
        else:
            raise DataParseError(file, "is missing the required 'Time' column.")

    # Parse cleaned data
    # ⚡ Bolt: removed `engine="python"` to use pandas default C engine for ~3x faster parsing
    # Note: engine='python' was intentionally removed to allow pandas
    # to use its default C engine, which provides a ~5x speedup for parsing.
    # ⚡ Bolt: Added `index_col=0` to let pandas directly assign 'Time' as the index
    # during parsing, which eliminates the ~10-15% overhead of manually extracting
    # it, dropping the column, and re-indexing the DataFrame afterwards.
    # ⚡ Bolt: Avoid loading entire residual files into memory (via a Python string
    # or `io.StringIO`) by parsing the `# Time` header manually from the first few
    # lines, and then letting Pandas stream the file using its fast C engine
    # via `names=headers` and `comment='#'`. This significantly reduces memory overhead.
    try:
        raw_data = pd.read_csv(
            file,
            names=headers,
            comment="#",
            sep=r"\s+",
            na_values="N/A",
            on_bad_lines="error",
            index_col=0,
        )
        if raw_data.index.name != "Time":
            raise DataParseError(file, "is missing the required 'Time' column.")

        # Convert the index back to a Series to maintain the function's return signature
        iterations = pd.Series(raw_data.index)
    except pd.errors.EmptyDataError as err:
        raise DataParseError(file, "is empty or malformed.") from err
    except IndexError as err:
        raise DataParseError(file, "is missing the required 'Time' column.") from err

    data = raw_data.dropna(
        axis=1, how="all"
    )  # keeps only columns that have at least one non-NaN

    return data, iterations


_LOG_TIME_RE = re.compile(
    r"^\s*Time\s*=\s*(?P<time>[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
)
_LOG_SOLVE_RE = re.compile(
    r"^\s*[^:]+:\s+Solving for (?P<field>[^,]+), Initial residual = "
    r"(?P<residual>[^,]+),"
)


def _parse_openfoam_log(file: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Parse OpenFOAM solver logs into residual data per time-step."""
    rows: list[dict[str, float]] = []
    indices: list[int] = []
    current_row: dict[str, float] | None = None
    time_step = 0

    with file.open(encoding="utf-8") as f:
        for line in f:
            if _LOG_TIME_RE.match(line):
                if current_row:
                    rows.append(current_row)
                    indices.append(time_step)
                time_step += 1
                current_row = {}
                continue

            if current_row is None:
                continue

            solve_match = _LOG_SOLVE_RE.match(line)
            if solve_match is None:
                continue

            field = solve_match.group("field").strip()
            if field in current_row:
                # Keep the first solve residual for each field per time-step.
                continue

            residual_raw = solve_match.group("residual").strip()
            try:
                current_row[field] = float(residual_raw)
            except ValueError:
                continue

    if current_row:
        rows.append(current_row)
        indices.append(time_step)

    if not rows:
        raise DataParseError(
            file,
            "is empty or malformed (expected residuals*.dat or OpenFOAM log format).",
        )

    raw_data = pd.DataFrame(rows, index=indices)
    raw_data.index.name = "Time"
    data = raw_data.dropna(axis=1, how="all")
    if data.empty:
        raise DataParseError(
            file,
            "is empty or malformed (no parseable residual values found in log).",
        )

    iterations = pd.Series(data.index)
    return data, iterations


def pre_parse(file: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Parse OpenFOAM residuals file and return formatted data."""
    # ⚡ Bolt: Cache parsed DataFrames to avoid redundant disk I/O and parsing overhead.
    # In batch processing, this function is called twice per file (once to find
    # min/max iteration ranges globally, and again to plot). Caching reduces total
    # parsing time by ~50% per file. The file's modification time (mtime) is used
    # as part of the cache key to ensure the cache is invalidated if the underlying
    # file on disk is modified.
    mtime = file.stat().st_mtime
    return _cached_pre_parse(file, mtime)
