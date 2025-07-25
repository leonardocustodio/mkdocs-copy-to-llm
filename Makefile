.PHONY: help install install-dev test lint format typecheck build clean

# Default target
help:
	@echo "MkDocs Copy to LLM - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install package in production mode"
	@echo "  make install-dev   Install package with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test          Run tests with coverage"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with Ruff"
	@echo "  make typecheck     Run type checking with MyPy"
	@echo ""
	@echo "Building:"
	@echo "  make build         Build distribution packages"
	@echo "  make clean         Clean build artifacts"

# Install package in production mode
install:
	pip install -e .

# Install package with development dependencies
install-dev:
	pip install -e ".[dev]"
	@echo "Installing pre-commit hooks..."
	pre-commit install

# Run tests with coverage
test:
	pytest -v --cov=mkdocs_copy_to_llm --cov-report=term-missing --cov-report=html

# Run linting checks
lint:
	ruff check mkdocs_copy_to_llm tests
	mypy mkdocs_copy_to_llm

# Format code
format:
	ruff format mkdocs_copy_to_llm tests
	ruff check --fix mkdocs_copy_to_llm tests

# Run type checking
typecheck:
	mypy mkdocs_copy_to_llm

# Build distribution packages
build: clean
	python -m build
	twine check dist/*

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
