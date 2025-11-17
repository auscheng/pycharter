#!/bin/bash
# Script to verify publishing setup is complete

echo "🔍 Verifying publishing setup..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: make install-dev"
    exit 1
fi

source venv/bin/activate

# Check required tools
echo "Checking required tools..."
MISSING=0

if ! python -c "import build" 2>/dev/null; then
    echo "❌ 'build' not installed"
    MISSING=1
else
    echo "✅ 'build' installed"
fi

if ! python -c "import twine" 2>/dev/null; then
    echo "❌ 'twine' not installed"
    MISSING=1
else
    echo "✅ 'twine' installed"
fi

if ! command -v twine > /dev/null 2>&1; then
    echo "⚠️  'twine' command not in PATH (but module exists)"
else
    echo "✅ 'twine' command available"
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo "✅ All publishing tools are installed!"
    echo ""
    echo "Next steps:"
    echo "  1. Get PyPI API token: https://pypi.org/manage/account/token/"
    echo "  2. Test build: make build"
    echo "  3. Test on TestPyPI: make publish-test"
    echo "  4. Publish to PyPI: make publish"
else
    echo "❌ Some tools are missing. Run: make install-dev"
    exit 1
fi

