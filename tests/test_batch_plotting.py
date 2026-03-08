"""Tests for batch plotting of OpenFOAM residual files."""

from __future__ import annotations

import pathlib
import unittest
from typing import ClassVar

import openfoam_residuals.filesystem as fs
import openfoam_residuals.plot as pl


class TestBatchPlotting(unittest.TestCase):
    """Verify that ``export_files`` discovers residual*.dat files, exports, and generates expected number of PNGs."""

    TEST_DIR: ClassVar[pathlib.Path]
    RESIDUAL_FILES: ClassVar[list[pathlib.Path]]
    EXPECTED_PNGS: ClassVar[int] = 14  # adjust when your fixture changes

    @classmethod
    def setUpClass(cls) -> None:
        """Locate fixture files once for the entire class."""
        cls.TEST_DIR = pathlib.Path(__file__).parent
        work_dir = cls.TEST_DIR / "files"

        cls.RESIDUAL_FILES = fs.find_residual_files(work_dir)
        # Fail fast if the fixture is missing
        assert cls.RESIDUAL_FILES, f"No residual files found in {work_dir}"

        min_val, max_iter = fs.find_min_and_max_iteration(cls.RESIDUAL_FILES)
        pl.export_files(
            cls.RESIDUAL_FILES,
            min_val,
            max_iter,
            output_dir=cls.TEST_DIR,
            colorblind=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up generated artefacts after all tests have run."""
        for png in cls.TEST_DIR.glob("*.png"):
            png.unlink(missing_ok=True)

    # ───────── actual assertions ─────────────────────────────────────────
    def test_png_export_count(self) -> None:
        """The exporter should create the expected number of PNG files."""
        pngs = list(self.TEST_DIR.glob("*.png"))
        assert len(pngs) == self.EXPECTED_PNGS, (
            f"Expected {self.EXPECTED_PNGS} PNGs, found {len(pngs)} in {self.TEST_DIR}"
        )

    def test_png_paths_exist(self) -> None:
        """Every file returned by glob should physically exist on disk."""
        for png in self.TEST_DIR.glob("*.png"):
            assert png.exists(), f"File {png} is missing"


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
