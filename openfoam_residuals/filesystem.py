"""Filesystem utilities for OpenFOAM residuals analysis."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from openfoam_residuals import utils


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
    raw_data = pd.read_csv(
        io.StringIO(cleaned_text),
        skiprows=[0],
        sep=r"\s+",
        engine="python",
        na_values="N/A",
        on_bad_lines="error",
    )
    iterations = raw_data["Time"]
    data = raw_data.drop(["Time"], axis=1)
    data = data.set_index(iterations)
    data = data.dropna(
        axis=1, how="all"
    )  # keeps only columns that have at least one non-NaN

    return data, iterations
