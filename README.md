# ipynb2html-pdf

[English](README.md) | [Español](README.es.md)

A professional Jupyter Notebook to HTML and PDF converter with a modern Python structure, CLI, and GUI.

## Features

- **Clean Conversion**: Automatically sanitizes notebooks by removing problematic metadata and widget states before conversion.
- **Dual Interface**: Use the simple Tkinter GUI or the powerful Command Line Interface (CLI).
- **Auto-Dependency Management**: Can optionally install missing Python packages (`nbconvert`, `pyppeteer`, etc.) and system packages (`pandoc` on Linux).
- **Professional Tooling**: Managed with `uv` and `just`.

## Quick Start

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (recommended) or [pip](https://pip.pypa.io/)
- [just](https://github.com/casey/just) (optional, for automation)
- **Tkinter** (For Linux users): `sudo apt-get install python3-tk`

### Installation

```bash
# Using uv
uv sync
```

### Usage

#### GUI

```bash
just gui
# OR
uv run ipynb2html-gui
```

#### CLI

```bash
just cli path/to/notebook.ipynb --to pdf
# OR
uv run ipynb2html path/to/notebook.ipynb --to html
```

## Development

We use `just` to manage common development tasks:

- `just setup`: Sync dependencies.
- `just lint`: Run Ruff checks and formatting.
- `just fix`: Automatically fix linting and formatting issues.
- `just test`: Run unit tests with Pytest.
- `just clean`: Remove temporary files.

## Project Structure

- `src/ipynb2html/`: Main package source code.
  - `converter.py`: Core logic for conversion and sanitization.
  - `cli.py`: Command-line interface.
  - `gui.py`: Graphical user interface.
- `tests/`: Unit tests.
- `pyproject.toml`: Project configuration and dependencies.
- `justfile`: Automation recipes.

## License

MIT
