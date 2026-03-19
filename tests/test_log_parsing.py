"""Tests for parsing OpenFOAM solver log files."""

from __future__ import annotations

from pathlib import Path

import pytest

import openfoam_residuals.filesystem as fs


def test_pre_parse_openfoam_log() -> None:
    """The parser should extract first residuals per field for each time-step."""
    log_file = Path(__file__).parent / "files" / "0" / "log.icoFoam.log"

    data, iterations = fs.pre_parse(log_file)

    assert not data.empty
    assert list(data.columns[:4]) == ["Ux", "Uy", "Uz", "p"]
    assert data.index[0] == 1
    assert iterations.iloc[0] == 1

    first_step = data.iloc[0]
    assert first_step["Ux"] == pytest.approx(1.0)
    assert first_step["Uy"] == pytest.approx(0.0)
    assert first_step["Uz"] == pytest.approx(0.0)
    assert first_step["p"] == pytest.approx(1.0)

    second_step = data.iloc[1]
    # The first pressure solve residual is kept when multiple p-solves exist.
    assert second_step["p"] == pytest.approx(0.00184376)
