## 2024-05-19 - Removed python engine from pandas read_csv
**Learning:** The default `pd.read_csv` behaviour when `engine="python"` is specified is significantly slower (~3x) when parsing many text files with simple white space delimiters.
**Action:** Let pandas use the default C engine (or specify `engine="c"`) unless there's a specific need for the python engine, such as regex delimiters that aren't single-character.

## 2025-02-13 - Pandas read_csv engine bottleneck
**Learning:** Using `sep=r"\s+"` in `pd.read_csv()` does NOT require `engine="python"`. The default C engine has special optimized support for `\s+` separator, and forcing `engine="python"` causes a significant (~5x) slowdown in parsing speed, particularly noticeable when reading large OpenFOAM residual files.
**Action:** When using `pd.read_csv` with `sep=r"\s+"`, ensure `engine="python"` is not unnecessarily specified, allowing pandas to use its faster default C parser.

## 2026-03-04 - Pandas dataframe plotting wrapper overhead
**Learning:** Calling `df.plot(ax=ax)` repeatedly in a loop is extremely slow because the pandas plotting API does a massive amount of boilerplate validation and formatting per call. Using matplotlib's native `ax.plot(df.index, df.values)` instead yields a >50% performance improvement.
**Action:** When batch-generating many plots, always extract the numpy arrays from pandas objects and use direct matplotlib functions (`ax.plot`, `ax.scatter`, etc.) rather than relying on pandas's higher-level wrapper.
