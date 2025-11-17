# Testing Guide

This guide explains how to run tests for the `pycharter` package.

## Prerequisites

Make sure you have:
1. Set up the development environment: `./setup.sh` or `make install-dev`
2. Activated the virtual environment: `source venv/bin/activate`

## Running Tests

### Using Makefile (Recommended)

The easiest way to run tests is using the Makefile commands:

```bash
# Run all tests (default)
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-cov

# Run only fast tests (exclude slow markers)
make test-fast

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration
```

### Using pytest Directly

You can also run pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_converter.py

# Run specific test function
pytest tests/test_converter.py::test_from_dict_simple_schema

# Run tests matching a pattern
pytest -k "test_coercion"

# Run with coverage
pytest --cov=pycharter --cov-report=html --cov-report=term

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests excluding slow ones
pytest -m "not slow"
```

## Test Configuration

Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`:

- **Test paths**: `tests/` directory
- **Test files**: Files matching `test_*.py`
- **Test classes**: Classes starting with `Test*`
- **Test functions**: Functions starting with `test_*`
- **Default options**: Verbose mode, short traceback format

## Test Markers

Tests can be marked with:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_converter.py        # Basic conversion tests
├── test_coercion_validation.py  # Coercion & validation tests
├── test_json_schema_compliance.py  # JSON Schema standard tests
├── test_x_validators.py     # x-validators format tests
├── test_refs_and_definitions.py  # $ref and definitions tests
├── test_reverse_conversion.py  # Pydantic → JSON Schema tests
├── test_schema_parser.py    # Schema parsing tests
├── test_integration.py      # Integration tests
├── test_fixtures.py         # Fixture usage examples
└── fixtures/                # Mock data and schemas
    ├── schemas/             # JSON schema fixtures
    └── sample_data/         # Sample data fixtures
```

## Running Specific Tests

### Run tests for a specific feature:

```bash
# Test coercion and validation
pytest tests/test_coercion_validation.py

# Test x-validators format
pytest tests/test_x_validators.py

# Test reverse conversion
pytest tests/test_reverse_conversion.py

# Test $ref and definitions
pytest tests/test_refs_and_definitions.py
```

### Run tests matching a keyword:

```bash
# All tests with "coercion" in the name
pytest -k coercion

# All tests with "validation" in the name
pytest -k validation

# All tests with "ref" in the name
pytest -k ref
```

## Coverage Reports

Generate coverage reports to see which code is tested:

```bash
# HTML coverage report
make test-cov
# Then open htmlcov/index.html in your browser

# Terminal coverage report only
pytest --cov=pycharter --cov-report=term

# Coverage with missing lines
pytest --cov=pycharter --cov-report=term-missing
```

## Debugging Tests

### Run with more verbose output:

```bash
# Very verbose (shows all test names)
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

### Run a single test in isolation:

```bash
# Run one test function
pytest tests/test_converter.py::test_from_dict_simple_schema -v

# Run with print statements visible
pytest tests/test_converter.py::test_from_dict_simple_schema -s
```

## Common Issues

### Issue: `pytest: command not found`
**Solution**: Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Issue: Tests fail with import errors
**Solution**: Install the package in development mode:
```bash
pip install -e ".[dev]"
```

### Issue: Tests pass locally but fail in CI
**Solution**: Make sure you're using the same Python version and dependencies. Check `pyproject.toml` for required Python version (>=3.10).

## Continuous Integration

Tests are configured to run automatically in CI/CD pipelines. The test suite includes:
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Tests for all major features (coercion, validation, $ref, x-validators, reverse conversion)

## Best Practices

1. **Run tests before committing**: `make test`
2. **Run tests with coverage**: `make test-cov` to ensure good coverage
3. **Write tests for new features**: Follow the existing test patterns
4. **Use fixtures**: Leverage `conftest.py` fixtures for reusable test data
5. **Mark slow tests**: Use `@pytest.mark.slow` for tests that take >1 second

## Quick Reference

```bash
# Most common commands
make test              # Run all tests
make test-verbose       # Run with verbose output
make test-cov          # Run with coverage
pytest -k "keyword"    # Run tests matching keyword
pytest path/to/test.py # Run specific test file
```

