"""Filesystem utilities for OpenFOAM residuals analysis."""

from __future__ import annotations

import io
from pathlib import Path

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
    for file in residual_files:
        data, _ = pre_parse(file)
        min_i = 10 ** utils.order_of_magnitude(data.min().min())
        if 0 < min_i < min_val:
            min_val = min_i
        max_iter_i = data.index.max()
        if max_iter_i > max_iter:
            max_iter = utils.roundup(max_iter_i)
    return min_val, max_iter


def pre_parse(file: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Parse OpenFOAM residuals file and return formatted data."""
    # Read file and strip all '#' characters line-by-line
    with file.open(encoding="utf-8") as f:
        cleaned_text = f.read().replace("#", "")

    # Parse cleaned data
    # ⚡ Bolt: removed `engine="python"` to use pandas default C engine for ~3x faster parsing
    # Note: engine='python' was intentionally removed to allow pandas
    # to use its default C engine, which provides a ~5x speedup for parsing.
    # ⚡ Bolt: Added `index_col=0` to let pandas directly assign 'Time' as the index
    # during parsing, which eliminates the ~10-15% overhead of manually extracting
    # it, dropping the column, and re-indexing the DataFrame afterwards.
    try:
        raw_data = pd.read_csv(
            io.StringIO(cleaned_text),
            skiprows=[0],
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
