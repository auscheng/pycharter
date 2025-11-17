# Quick Start Guide

## Fastest Setup (3 commands)

```bash
# 1. Run setup script
./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Test it works
pytest
```

That's it! 🎉

## Alternative: Using Make

```bash
make install-dev    # One command to set everything up
source venv/bin/activate
make test          # Run tests
```

## Alternative: Using uv (Fastest)

If you have `uv` installed (modern Python package manager):

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## What Gets Installed?

- **pycharter** package (in editable/development mode)
- **Development tools**: pytest, black, isort, mypy, build, twine
- **Virtual environment**: Isolated from your system Python

## Verify Installation

```bash
pytest
```

## Daily Workflow

```bash
# Activate environment
source venv/bin/activate

# Make changes to code...

# Run tests
pytest

# Format code
make format

# Run all checks
make check
```

