# Default recipe: list available recipes
default:
    @just --list

# Install all dependencies (including dev)
sync:
    uv sync --all-extras --dev

# Run linter
lint:
    uv run ruff check src/ packages/ pytest/ scripts/

# Run linter and auto-fix
lint-fix:
    uv run ruff check --fix src/ packages/ pytest/ scripts/

# Format code
fmt:
    uv run ruff format src/ packages/ pytest/ scripts/

# Run tests
test:
    uv run pytest

# Run tests with verbose output
test-verbose:
    uv run pytest -v

# Serve docs locally with live reload (opens browser)
docs-serve:
    uv run zensical serve --config-file docs/zensical.toml -o

# Build docs as a static site
docs-build:
    uv run zensical build --config-file docs/zensical.toml

# Copy built wheels into the docs site
docs-copy-wheels:
    uv run python docs/scripts/build_docs_wheels.py

# Build all releasable distributions
build-release:
    uv build --package mcqpy
    uv build --package mcqpy-core
    uv build --package mcqpy-pdf
    uv build --package mcqpy-shiny

# Run isolated smoke tests against built distributions
smoke-release:
    uv run python scripts/release/smoke_built_distributions.py

# List built distribution files whose versions are not yet on PyPI
select-release-files:
    uv run python scripts/release/select_publish_files.py

# Remove the built docs output
docs-clean:
    rm -rf docs/site
