"""Utility functions for OpenFOAM residuals analysis."""

from __future__ import annotations

import math

import numpy as np


def order_of_magnitude(number: float) -> int:
    """Return the order of magnitude of a number."""
    if np.isnan(number):
        return 0
    return math.floor(math.log10(number))


def roundup(x: float) -> int:
    """Round up to the next hundred."""
    return math.ceil(x / 100.0) * 100
