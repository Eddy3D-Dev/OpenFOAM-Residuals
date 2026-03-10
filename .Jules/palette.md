## 2026-03-02 - Expose Examples in CLI Help
**Learning:** Command-line tools often have great usage examples in their module docstrings, but they are hidden from users. Exposing them in `--help` provides significant onboarding value.
**Action:** Use `argparse.RawDescriptionHelpFormatter` with `epilog=__doc__` to automatically surface module docstrings as examples in CLI help outputs.

## 2026-03-03 - Expose Path Context in Batch Processing
**Learning:** In batch processing CLIs where multiple identically named files (e.g., `residuals.dat`) are being processed, displaying only the filename in the progress indicator offers no context. Users can't tell which specific task or folder is currently processing.
**Action:** When logging progress, display a few parent directories of the file path (e.g., using `"/".join(path.parts[-3:])`) rather than just the filename to give meaningful feedback.

## 2026-03-03 - Unify Redundant CLI Success States
**Learning:** Redundant success messages (e.g., "Complete!" followed immediately by "Successfully exported X to Y") create visual clutter and reduce the perceived polish of a CLI tool.
**Action:** When clearing progress indicators, avoid appending an additional success message if the main caller already prints a comprehensive final success state. Always include metrics (like the number of files processed) in the final success message to provide maximum value.

## 2026-03-04 - Provide Progress Context During Data Parsing
**Learning:** Silent data-processing phases before actual feedback (like plotting) feel like hangs. Users should get immediate feedback when files are discovered and receive progress indicators during parsing.
**Action:** Move initialization messages to right before processing starts and provide a progress indicator (`last 3 path components`) during data parsing too.

## 2026-03-04 - Colored Terminal Outputs
**Learning:** Pure CLI tools lack visual hierarchy, making it difficult for users to distinguish errors from informational messages at a glance. Adding ANSI color codes to log levels drastically improves the developer experience with zero additional dependency weight.
**Action:** When working on CLI tools, implement native ANSI color formatting for console outputs connected to a TTY to provide immediate, accessible visual cues.

## 2026-03-04 - Clean Progress Indicators and Exception Handling
**Learning:** In terminal CLIs, inline progress indicators (`\r`) can cause visual flickering of the cursor. Furthermore, exceptions raised during progress can interleave with the progress text, creating confusing and unreadable error logs.
**Action:** Always hide the cursor (`\033[?25l`) while progress is active, and ensure it is restored on exit (e.g., via `atexit`). When handling top-level exceptions, clear the current progress line (`\r\033[K`) before logging the error to maintain clean output.

## 2026-03-05 - Avoid Silent Directory Traversals
**Learning:** Silent directory transversals or async filesystem blocking operations can leave users feeling that the application has frozen. Waiting for subsequent progress indications (like plotting) is not sufficient since finding the files itself could take a while in large directories.
**Action:** Add visual loading indicators like `\r\033[K📁 Scanning '<dir>'...` whenever recursively searching or blocking on large directory operations.

## 2026-03-05 - Enhance Readability of Logarithmic Plots
**Learning:** When using logarithmic scales, reading values and distinguishing data points across orders of magnitude becomes difficult without visual aids.
**Action:** Always enable both major and minor gridlines on logarithmic axes (e.g., `ax.grid(visible=True, which="major", alpha=0.6)`) to provide crucial spatial context and improve data readability.

## 2026-03-08 - Use Colorblind-Friendly Palettes for Data Visualization
**Learning:** Default color cycles in plotting libraries often rely on combinations of red, green, and other colors that are indistinguishable for users with various forms of color vision deficiency (e.g., deuteranomaly, protanomaly). When plotting complex data like OpenFOAM residuals with multiple lines, this makes the visualization completely inaccessible to a significant portion of the population.
**Action:** Always explicitly apply a colorblind-friendly style or palette (like `tableau-colorblind10` in matplotlib) before generating data visualizations to ensure accessibility without sacrificing aesthetics.

## 2026-03-09 - Move Legends Outside Data-Dense Plots
**Learning:** In data-dense plots (like OpenFOAM residuals), placing the legend inside the plot area (`loc="upper right"`) frequently obscures critical data points (such as high initial residuals), leading to a frustrating user experience.
**Action:** When creating dense visualizations, always place the legend outside the primary plot area (e.g., `ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")`) and ensure the output captures it by using `bbox_inches="tight"` during export.

## 2026-03-10 - Use Varying Line Styles for Data Visualization
**Learning:** Depending solely on color to differentiate between multiple lines in a plot makes the visualization inaccessible to users with color vision deficiency, and completely illegible if printed in grayscale.
**Action:** Always combine color differences with varying line styles (e.g., solid, dashed, dotted, dashdot) when generating multi-line plots to ensure the data can be distinguished through multiple visual channels.
