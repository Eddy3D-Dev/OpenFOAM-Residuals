## 2024-05-19 - Removed python engine from pandas read_csv
**Learning:** The default `pd.read_csv` behaviour when `engine="python"` is specified is significantly slower (~3x) when parsing many text files with simple white space delimiters.
**Action:** Let pandas use the default C engine (or specify `engine="c"`) unless there's a specific need for the python engine, such as regex delimiters that aren't single-character.

## 2025-02-13 - Pandas read_csv engine bottleneck
**Learning:** Using `sep=r"\s+"` in `pd.read_csv()` does NOT require `engine="python"`. The default C engine has special optimized support for `\s+` separator, and forcing `engine="python"` causes a significant (~5x) slowdown in parsing speed, particularly noticeable when reading large OpenFOAM residual files.
**Action:** When using `pd.read_csv` with `sep=r"\s+"`, ensure `engine="python"` is not unnecessarily specified, allowing pandas to use its faster default C parser.

## 2026-03-04 - Pandas `.min().min()` overhead on large DataFrames
**Learning:** Computing the global minimum of a pandas DataFrame using `df.min().min()` is surprisingly slow because it computes the minimum per column (creating a new Series) before computing the global minimum. Converting the numeric DataFrame to a numpy array first via `df.to_numpy()` and using `numpy.nanmin()` is ~20x faster. Additionally, for monotonically increasing index values (like OpenFOAM Time iterations), getting the max index using `df.index[-1]` avoids the O(N) cost of `df.index.max()`.
**Action:** When computing a global scalar statistic (like `min` or `max`) over an entire numeric DataFrame, always convert it to a NumPy array first (`np.nanmin(df.to_numpy())`) to bypass pandas indexing and structure overhead. For sorted indices, use positional indexing (`[-1]`) instead of a full scan.
