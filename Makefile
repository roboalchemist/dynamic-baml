# Makefile for dynamic_baml package

.PHONY: init test clean install build upload docs help lint format

# Default target
help:
	@echo "Available targets:"
	@echo "  init           - Install development dependencies"
	@echo "  test           - Run unit tests with coverage"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests with gemma3:1b"
	@echo "  test-all       - Run all tests (unit + integration)"
	@echo "  clean          - Remove build artifacts and cache files"
	@echo "  install        - Install package in development mode"
	@echo "  build          - Build distribution packages"
	@echo "  upload         - Upload to PyPI (requires credentials)"
	@echo "  docs           - Build documentation"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black"

# Install development dependencies
init:
	pip install -r requirements.txt
	pip install -e .[dev,docs]

# Run tests with coverage
test:
	pytest tests/ --cov=dynamic_baml --cov-report=html --cov-report=term-missing -m "not integration"
	@echo "Coverage report saved to htmlcov/index.html"

# Run unit tests only (no integration)
test-unit:
	pytest tests/ --cov=dynamic_baml --cov-report=html --cov-report=term-missing -m "not integration"
	@echo "Unit tests completed"

# Run integration tests with actual models
test-integration:
	./test_integration.sh

# Run all tests including integration
test-all:
	pytest tests/ --cov=dynamic_baml --cov-report=html --cov-report=term-missing
	@echo "All tests completed (unit + integration)"

# Clean build artifacts and cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf docs/_build/

# Install package in development mode
install:
	pip install -e .

# Build distribution packages
build: clean
	python -m build

# Upload to PyPI (test first with: make upload REPO=testpypi)
upload: build
	python -m twine upload $(if $(REPO),--repository $(REPO)) dist/*

# Build documentation
docs:
	cd docs && make html
	@echo "Documentation built in docs/_build/html/"

# Run code linting
lint:
	flake8 dynamic_baml tests examples
	mypy dynamic_baml

# Format code with black
format:
	black dynamic_baml tests examples
	isort dynamic_baml tests examples

# Run all quality checks
check: lint test
	@echo "All quality checks passed!"

# Development setup
dev-setup: init
	pre-commit install
	@echo "Development environment setup complete!" 