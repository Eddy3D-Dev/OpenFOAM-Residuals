## 2026-03-02 - Expose Examples in CLI Help
**Learning:** Command-line tools often have great usage examples in their module docstrings, but they are hidden from users. Exposing them in `--help` provides significant onboarding value.
**Action:** Use `argparse.RawDescriptionHelpFormatter` with `epilog=__doc__` to automatically surface module docstrings as examples in CLI help outputs.

## 2026-03-03 - Unify Redundant CLI Success States
**Learning:** Redundant success messages (e.g., "Complete!" followed immediately by "Successfully exported X to Y") create visual clutter and reduce the perceived polish of a CLI tool.
**Action:** When clearing progress indicators, avoid appending an additional success message if the main caller already prints a comprehensive final success state. Always include metrics (like the number of files processed) in the final success message to provide maximum value.
