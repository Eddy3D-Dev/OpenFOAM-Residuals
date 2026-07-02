## 2024-06-25 - Redundant NaN check with Numpy inequalities
**Learning:** In numpy, boolean inequalities (like `values > 0`) intrinsically evaluate to `False` for `np.nan` values. Adding an explicit `& ~np.isnan(values)` check is entirely redundant and slows down execution by forcing a second pass over the array and a bitwise operation.
**Action:** Avoid redundant `np.isnan` checks when filtering numpy arrays with inequalities.
