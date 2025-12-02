[![Python package](https://github.com/Eddy3D-Dev/OpenFOAM-Residuals/actions/workflows/main.yml/badge.svg)](https://github.com/Eddy3D-Dev/OpenFOAM-Residuals/actions/workflows/main.yml) ![GitHub Tag](https://img.shields.io/github/v/tag/Eddy3D-Dev/OpenFOAM-Residuals)

# OpenFOAM-Residuals

A Python tool to parse and plot residual data from OpenFOAM case directories. This tool is designed to work with output from [Eddy3D](https://www.eddy3d.com), an airflow and microclimate simulation plugin for Rhino and Grasshopper, but can be used with standard OpenFOAM residual files as well.

## Features

-   **Automatic Detection**: Recursively finds `residuals*.dat` files in case directories.
-   **Batch Processing**: Handle multiple case directories or single files.
-   **Plotting**: Generates high-quality PNG plots of residuals vs. iterations.
-   **Data Export**: Exports cleaned data for further analysis.
-   **Smart Scaling**: Automatically adjusts plot scales based on residual magnitude.

## Installation

This project uses `uv` for dependency management.

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/Eddy3D-Dev/OpenFOAM-Residuals.git
    cd OpenFOAM-Residuals
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

You can run the tool directly using `uv run`:

### Single File
Plot residuals for a specific file:
```bash
uv run python -m openfoam_residuals.main -f /path/to/residuals.dat
```

### Case Directory
Automatically find and plot all residual files in a directory (recursive):
```bash
uv run python -m openfoam_residuals.main -w /path/to/case/dir
```

### Multiple Directories
Process multiple case directories at once:
```bash
uv run python -m openfoam_residuals.main -w case1 -w case2
```

### Options
-   `-o`, `--out`: Specify output directory (default: `exports`).
-   `--no-plots`: Skip plot generation and only export data.
-   `-v`, `--verbose`: Increase logging verbosity (e.g., `-vv`).

## Development

### Running Tests
```bash
uv run pytest
```

### Linting and Formatting
```bash
uv run ruff check
uv run ruff format
```

## License

GNU General Public License v3 (GPLv3)
