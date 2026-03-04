## 2026-03-02 - Expose Examples in CLI Help
**Learning:** Command-line tools often have great usage examples in their module docstrings, but they are hidden from users. Exposing them in `--help` provides significant onboarding value.
**Action:** Use `argparse.RawDescriptionHelpFormatter` with `epilog=__doc__` to automatically surface module docstrings as examples in CLI help outputs.

## 2026-03-03 - Expose Path Context in Batch Processing
**Learning:** In batch processing CLIs where multiple identically named files (e.g., `residuals.dat`) are being processed, displaying only the filename in the progress indicator offers no context. Users can't tell which specific task or folder is currently processing.
**Action:** When logging progress, display a few parent directories of the file path (e.g., using `"/".join(path.parts[-3:])`) rather than just the filename to give meaningful feedback.

## 2026-03-03 - Unify Redundant CLI Success States
**Learning:** Redundant success messages (e.g., "Complete!" followed immediately by "Successfully exported X to Y") create visual clutter and reduce the perceived polish of a CLI tool.
**Action:** When clearing progress indicators, avoid appending an additional success message if the main caller already prints a comprehensive final success state. Always include metrics (like the number of files processed) in the final success message to provide maximum value.

## 2026-03-04 - Colored Terminal Outputs
**Learning:** Pure CLI tools lack visual hierarchy, making it difficult for users to distinguish errors from informational messages at a glance. Adding ANSI color codes to log levels drastically improves the developer experience with zero additional dependency weight.
**Action:** When working on CLI tools, implement native ANSI color formatting for console outputs connected to a TTY to provide immediate, accessible visual cues.
