"""Utility functions for OpenFOAM residuals analysis."""

from __future__ import annotations

import math
import shutil

import numpy as np


def order_of_magnitude(number: float) -> int:
    """Return the order of magnitude of a number."""
    if np.isnan(number):
        return 0
    return math.floor(math.log10(number))


def roundup(x: float) -> int:
    """Round up to the next hundred."""
    return math.ceil(x / 100.0) * 100


def truncate_path(path_str: str, base_msg_len: int = 0) -> str:
    """Truncate a path string to fit within the terminal width."""
    term_cols = shutil.get_terminal_size().columns
    avail = term_cols - base_msg_len - 6  # 6 for " ()..." or similar wrapping chars
    if avail > 5 and len(path_str) > avail:
        return "…" + path_str[-(avail - 1) :]
    return path_str
