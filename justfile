# Default recipe: list available recipes
default:
    @just --list

# Install all dependencies (including dev)
sync:
    uv sync

# Run linter
lint:
    uv run ruff check src/ pytest/ tests/

# Run linter and auto-fix
lint-fix:
    uv run ruff check --fix src/ pytest/ tests/

# Format code
fmt:
    uv run ruff format src/ pytest/ tests/

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

# Remove the built docs output
docs-clean:
    rm -rf docs/site
