# Testing PyCharter in Jupyter Notebooks

This guide explains how to test the pycharter package locally in Jupyter notebooks.

## Quick Start

### 1. Install the Package in Development Mode

From the project root directory:

```bash
# Activate your virtual environment (if using one)
source venv/bin/activate  # or: . venv/bin/activate

# Install in editable mode (changes to code are reflected immediately)
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### 2. Set Up Jupyter Kernel

Make sure your Jupyter notebook kernel is using the same Python environment where you installed the package.

#### Option A: Using the Virtual Environment's Python

If you're using a virtual environment:

```bash
# Install jupyter in your venv
pip install jupyter ipykernel

# Create a kernel for this environment
python -m ipykernel install --user --name=pycharter-dev --display-name "Python (pycharter-dev)"

# Start Jupyter
jupyter notebook
```

Then select the "Python (pycharter-dev)" kernel in your notebook.

#### Option B: Using System Python

If you installed directly to system Python:

```bash
# Just start Jupyter
jupyter notebook
```

### 3. Test the Package

Open `test_pycharter.ipynb` in this directory and run all cells. This notebook contains comprehensive tests covering:

- Basic schema conversion
- Standard JSON Schema keywords
- Nested objects
- Arrays
- Coercion and validation
- Loading from files and JSON strings
- Error handling

## Verification

To verify the package is installed correctly:

```python
import pycharter
import os

print(f"Version: {pycharter.__version__}")
print(f"Package location: {os.path.dirname(pycharter.__file__)}")
```

If you see the package location pointing to your local directory (not site-packages), the editable install is working!

## Development Workflow

1. **Make changes** to the package code in `pycharter/`
2. **Restart the kernel** in your notebook (Kernel → Restart)
3. **Re-run cells** to test your changes

The editable install (`pip install -e .`) means you don't need to reinstall after every change, but you do need to restart the kernel to reload the module.

## Troubleshooting

### "ModuleNotFoundError: No module named 'pycharter'"

**Solution**: Make sure:
1. The package is installed: `pip install -e .`
2. Your notebook kernel is using the same Python environment
3. You've restarted the kernel after installation

### Changes Not Reflecting

**Solution**: 
1. Make sure you installed with `-e` flag (editable mode)
2. Restart the Jupyter kernel (Kernel → Restart)
3. Re-run the import cell

### Wrong Python Environment

**Solution**: 
1. Check which Python your kernel is using:
   ```python
   import sys
   print(sys.executable)
   ```
2. Install the package in that environment:
   ```bash
   /path/to/kernel/python -m pip install -e /path/to/pycharter
   ```

## Example Usage

```python
from pycharter import from_dict

# Define schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name"]
}

# Generate model
Person = from_dict(schema, "Person")

# Use it
person = Person(name="Alice", age=30)
print(person.name)  # Output: Alice
```

## Additional Resources

- See `test_charter.ipynb` for comprehensive examples
- Check `../examples/` for more schema examples
- Read `../README.md` for full documentation

