.PHONY: install install-dev install-all run test lint format clean build

# Default target
help:
	@echo "OpenSati Development Commands"
	@echo "=============================="
	@echo ""
	@echo "  make install      Install OpenSati (basic)"
	@echo "  make install-dev  Install with dev dependencies"
	@echo "  make install-all  Install all optional dependencies"
	@echo "  make run          Run OpenSati"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linter"
	@echo "  make format       Format code"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build distribution"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all]"

install-audio:
	pip install -e ".[audio]"

# Running
run:
	python -m opensati

# Development
test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

# Building
build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# AI Setup
setup-ai:
	@echo "Setting up local AI models..."
	ollama pull llama3
	ollama pull llava
	@echo "Done! AI models are ready."

# Full setup
setup: install setup-ai
	@echo "OpenSati is ready! Run with: make run"
