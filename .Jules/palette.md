## 2026-03-02 - Expose Examples in CLI Help
**Learning:** Command-line tools often have great usage examples in their module docstrings, but they are hidden from users. Exposing them in `--help` provides significant onboarding value.
**Action:** Use `argparse.RawDescriptionHelpFormatter` with `epilog=__doc__` to automatically surface module docstrings as examples in CLI help outputs.

## 2026-03-03 - Expose Path Context in Batch Processing
**Learning:** In batch processing CLIs where multiple identically named files (e.g., `residuals.dat`) are being processed, displaying only the filename in the progress indicator offers no context. Users can't tell which specific task or folder is currently processing.
**Action:** When logging progress, display a few parent directories of the file path (e.g., using `"/".join(path.parts[-3:])`) rather than just the filename to give meaningful feedback.
