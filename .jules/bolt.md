## 2025-02-13 - Pandas read_csv engine bottleneck
**Learning:** Using `sep=r"\s+"` in `pd.read_csv()` does NOT require `engine="python"`. The default C engine has special optimized support for `\s+` separator, and forcing `engine="python"` causes a significant (~5x) slowdown in parsing speed, particularly noticeable when reading large OpenFOAM residual files.
**Action:** When using `pd.read_csv` with `sep=r"\s+"`, ensure `engine="python"` is not unnecessarily specified, allowing pandas to use its faster default C parser.
