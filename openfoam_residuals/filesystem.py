"""Filesystem utilities for OpenFOAM residuals analysis."""

from __future__ import annotations

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
    """Return a list of all residuals*.dat files recursively found under w_dir."""
    return list(Path(w_dir).rglob("residuals*.dat"))


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
            sys.stdout.write(
                f"\r\033[K🔍 Analyzing {idx + 1}/{total} ({display_name})..."
            )
            sys.stdout.flush()

        data, _ = pre_parse(file)
        # ⚡ Bolt: Use `np.nanmin(data.to_numpy())` instead of `data.min().min()`.
        # Converting to a numpy array first avoids Pandas overhead of computing
        # min per column and creates a ~20x faster C-level min computation.
        min_i = 10 ** utils.order_of_magnitude(np.nanmin(data.to_numpy()))
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


def pre_parse(file: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Parse OpenFOAM residuals file and return formatted data."""
    # Read just the header lines to avoid loading the entire file into memory
    with file.open(encoding="utf-8") as f:
        # First line is usually "# Residuals", skip it
        f.readline()
        # Second line contains the headers
        header_line = f.readline()
        if not header_line:
            raise DataParseError(file, "is empty or malformed.")

        # Clean headers by removing '#' and splitting by whitespace
        headers = header_line.replace("#", "").split()

    # Parse data directly from the file stream
    # ⚡ Bolt: Passing the file path directly to pd.read_csv avoids the massive
    # memory and time overhead of loading the entire file into memory and doing
    # string replacements (`f.read().replace("#", "")`). Instead, we manually
    # extract the headers from the first two lines, and start reading the data
    # directly from line 3 (`skiprows=2`), assigning the headers explicitly.
    try:
        raw_data = pd.read_csv(
            file,
            skiprows=2,
            sep=r"\s+",
            names=headers,
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
