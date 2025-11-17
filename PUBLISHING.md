# Publishing to PyPI

This guide walks you through publishing the `pycharter` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account**: Create an account at https://test.pypi.org/account/register/ (for testing)
3. **API Token**: Generate an API token at https://pypi.org/manage/account/token/ (recommended) or use username/password

## Step-by-Step Publishing Process

### 1. Prepare Your Package

```bash
# Make sure you're in the project directory
cd pycharter

# Activate your virtual environment
source venv/bin/activate

# Run all checks before publishing
make check
# or manually:
pytest
make format
make lint
```

### 2. Update Version Number

Before publishing, update the version in `pyproject.toml`:

```toml
version = "0.0.1"  # Change this to your new version
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes

### 3. Clean Previous Builds

```bash
make clean
# or manually:
rm -rf build/ dist/ *.egg-info
```

### 4. Build the Package

```bash
# Install build tools if not already installed
pip install build twine

# Build the package
make build
# or manually:
python -m build
```

This creates:
- `dist/pycharter-0.0.1.tar.gz` (source distribution)
- `dist/pycharter-0.0.1-py3-none-any.whl` (wheel distribution)

### 5. Test on TestPyPI (Recommended)

**First time setup:**
```bash
# Create ~/.pypirc file (optional, for convenience)
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestPyPITokenHere

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YourPyPITokenHere
EOF
chmod 600 ~/.pypirc
```

**Upload to TestPyPI:**
```bash
# Using twine with TestPyPI
twine upload --repository testpypi dist/*

# Or if you set up .pypirc:
twine upload --repository testpypi dist/*
```

**Test the installation:**
```bash
# Create a fresh virtual environment to test
python3 -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycharter

# Test it works
python -c "from pycharter import from_dict; schema = {'type': 'object', 'properties': {'name': {'type': 'string'}}}; Model = from_dict(schema, 'Test'); print('✓ Package works!')"

# Clean up
deactivate
rm -rf test_env
```

### 6. Publish to PyPI

Once you've tested on TestPyPI and everything works:

```bash
# Upload to PyPI
twine upload dist/*

# Or if using .pypirc:
twine upload --repository pypi dist/*
```

You'll be prompted for credentials:
- **Username**: `__token__` (if using API token)
- **Password**: Your PyPI API token (starts with `pypi-`)

### 7. Verify Publication

Visit your package page:
```
https://pypi.org/project/pycharter/
```

Test installation:
```bash
pip install pycharter
python -c "from pycharter import from_dict; schema = {'type': 'object', 'properties': {'name': {'type': 'string'}}}; Model = from_dict(schema, 'Test'); print('✓ Package works!')"
```

## Using API Tokens (Recommended)

API tokens are more secure than passwords:

1. Go to https://pypi.org/manage/account/token/
2. Create a new token (scope: "Entire account" or project-specific)
3. Copy the token (starts with `pypi-`)
4. Use it as the password when uploading, or set it in `~/.pypirc`

## Quick Commands (Using Make)

```bash
# Build the package
make build

# Clean build artifacts
make clean

# Build and check (before publishing)
make check
```

## Troubleshooting

### Package name already exists
- The name `pycharter` might be taken on PyPI
- Check availability at https://pypi.org/project/pycharter/
- If taken, change the name in `pyproject.toml` under `[project] name = "your-unique-name"`

### Authentication errors
- Make sure you're using the correct token/credentials
- For API tokens, username must be `__token__`
- Check token hasn't expired

### Version already exists
- You can't re-upload the same version
- Increment the version number in `pyproject.toml`

### Build errors
- Make sure all required files are included (check `MANIFEST.in`)
- Verify `pyproject.toml` is valid
- Run `make clean` and try again

## Automated Publishing (Optional)

For CI/CD, you can automate publishing using GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## Next Steps After Publishing

1. Create a GitHub release with the same version number
2. Update your documentation
3. Announce your package (Reddit, Twitter, etc.)
4. Monitor for issues and feedback

