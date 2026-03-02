## 2026-03-02 - Expose Examples in CLI Help
**Learning:** Command-line tools often have great usage examples in their module docstrings, but they are hidden from users. Exposing them in `--help` provides significant onboarding value.
**Action:** Use `argparse.RawDescriptionHelpFormatter` with `epilog=__doc__` to automatically surface module docstrings as examples in CLI help outputs.
