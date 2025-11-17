#!/bin/bash
# Quick setup script for pycharter development environment

set -e  # Exit on error

echo "🚀 Setting up pycharter development environment..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📦 Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📝 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install package in development mode with dev dependencies
echo "📥 Installing pycharter in development mode with dev dependencies..."
pip install -e ".[dev]" --quiet

# Install Jupyter Lab and ipykernel for notebook support
echo "📚 Installing Jupyter Lab and ipykernel for notebook support..."
pip install jupyterlab ipykernel --quiet

# Create Jupyter kernel for this environment
KERNEL_NAME="pycharter-dev"
KERNEL_DISPLAY_NAME="Python (pycharter-dev)"

echo "🔧 Setting up Jupyter kernel..."
# Remove existing kernel if it exists (ignore errors)
jupyter kernelspec remove "$KERNEL_NAME" --quiet 2>/dev/null || true

# Create new kernel
python -m ipykernel install --user --name="$KERNEL_NAME" --display-name="$KERNEL_DISPLAY_NAME"

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📓 Jupyter Lab Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start Jupyter Lab:"
echo "  1. Activate the environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start Jupyter Lab:"
echo "     jupyter lab"
echo ""
echo "  3. In your notebook, select the kernel:"
echo "     '$KERNEL_DISPLAY_NAME'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To test the installation:"
echo "  pytest"
echo ""
echo "To test in a notebook:"
echo "  Open notebooks/test_pycharter.ipynb"
echo "  Select kernel: '$KERNEL_DISPLAY_NAME'"
echo "  Run all cells"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Development Tips"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "• The package is installed in editable mode (-e), so code changes are"
echo "  reflected immediately (just restart the kernel in Jupyter)"
echo ""
echo "• To verify the kernel is using the right environment, run in a notebook:"
echo "  import sys; print(sys.executable)"
echo ""
echo "• To list all available kernels:"
echo "  jupyter kernelspec list"
echo ""

