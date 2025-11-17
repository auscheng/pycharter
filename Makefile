.PHONY: help install install-dev test clean build format lint type-check publish publish-test

# Detect if venv exists and set PYTHON/PIP accordingly
ifeq ($(wildcard venv/bin/python),)
    PYTHON := python3
    PIP := pip3
    PYTHON_CMD := python3 -m
else
    PYTHON := venv/bin/python
    PIP := venv/bin/pip
    PYTHON_CMD := venv/bin/python -m
endif

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -e .

install-dev: ## Install package + all development dependencies
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"
	@echo "To activate: source venv/bin/activate"

test: ## Run tests
	$(PYTHON_CMD) pytest

test-verbose: ## Run tests with verbose output
	$(PYTHON_CMD) pytest -v

test-cov: ## Run tests with coverage
	$(PYTHON_CMD) pytest --cov=pycharter --cov-report=html --cov-report=term

test-fast: ## Run fast tests only (exclude slow markers)
	$(PYTHON_CMD) pytest -m "not slow"

test-unit: ## Run unit tests only
	$(PYTHON_CMD) pytest -m "unit"

test-integration: ## Run integration tests only
	$(PYTHON_CMD) pytest -m "integration"

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

build: ## Build distribution packages
	@if [ ! -d "venv" ]; then \
		echo "⚠️  Warning: venv not found. Using system python."; \
		echo "💡 Tip: Run 'make install-dev' first to set up the development environment."; \
	fi
	@if ! $(PYTHON) -c "import build" 2>/dev/null; then \
		echo "❌ Error: 'build' module not found. Install it with: pip install build"; \
		echo "💡 Or run 'make install-dev' to set up the development environment."; \
		exit 1; \
	fi
	$(PYTHON_CMD) build

format: ## Format code with black and isort
	@if [ -f "venv/bin/black" ]; then \
		venv/bin/black pycharter tests && venv/bin/isort pycharter tests; \
	else \
		black pycharter tests && isort pycharter tests; \
	fi

lint: ## Run linting checks
	@if [ -f "venv/bin/black" ]; then \
		venv/bin/black --check pycharter tests && venv/bin/isort --check pycharter tests; \
	else \
		black --check pycharter tests && isort --check pycharter tests; \
	fi

type-check: ## Run type checking with mypy
	@if [ -f "venv/bin/mypy" ]; then \
		venv/bin/mypy pycharter; \
	else \
		mypy pycharter; \
	fi

check: format lint type-check test ## Run all checks (format, lint, type-check, test)

publish-test: clean build ## Build and upload to TestPyPI (for testing)
	@echo "Uploading to TestPyPI..."
	@if [ -f "venv/bin/twine" ] && venv/bin/twine --version > /dev/null 2>&1; then \
		venv/bin/twine upload --repository testpypi dist/*; \
	elif command -v twine > /dev/null 2>&1; then \
		twine upload --repository testpypi dist/*; \
	else \
		echo "❌ Error: 'twine' not found. Install it with: pip install twine"; \
		echo "💡 Or run 'make install-dev' to set up the development environment."; \
		exit 1; \
	fi
	@echo "Test installation with: pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycharter"

publish: clean build ## Build and upload to PyPI (production)
	@echo "⚠️  WARNING: This will publish to PyPI!"
	@echo "Make sure you've tested on TestPyPI first (make publish-test)"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read dummy
	@if [ -f "venv/bin/twine" ] && venv/bin/twine --version > /dev/null 2>&1; then \
		venv/bin/twine upload dist/*; \
	elif command -v twine > /dev/null 2>&1; then \
		twine upload dist/*; \
	else \
		echo "❌ Error: 'twine' not found. Install it with: pip install twine"; \
		echo "💡 Or run 'make install-dev' to set up the development environment."; \
		exit 1; \
	fi
	@echo "✅ Published! Check https://pypi.org/project/pycharter/"

