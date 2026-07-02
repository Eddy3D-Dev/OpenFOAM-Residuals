## 2024-06-25 - Redundant NaN check with Numpy inequalities
**Learning:** In numpy, boolean inequalities (like `values > 0`) intrinsically evaluate to `False` for `np.nan` values. Adding an explicit `& ~np.isnan(values)` check is entirely redundant and slows down execution by forcing a second pass over the array and a bitwise operation.
**Action:** Avoid redundant `np.isnan` checks when filtering numpy arrays with inequalities.
## 2024-07-02 - Filesystem traversal performance
**Learning:** Multiple `Path.rglob` calls on the same directory tree cause redundant I/O overhead. This is especially pronounced in large simulation directories where file counts are high.
**Action:** Always combine multi-pattern filesystem searches into a single pass using `os.walk` paired with fast string matching (`startswith`, `endswith`) to minimize disk I/O.
