# ipynb2html-pdf justfile

# Install dependencies and set up the environment
setup:
    uv sync

# Run the GUI application
gui:
    uv run ipynb2html-gui

# Run the CLI
cli *args:
    uv run ipynb2html {{args}}

# Run linting and formatting checks
lint:
    uv run ruff check .
    uv run ruff format --check .

# Fix linting and formatting issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run unit tests
test:
    uv run pytest

# Clean up temporary files
clean:
    rm -rf .pytest_cache .ruff_cache build dist *.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.clean" -delete

# Build the package
build:
    uv build
