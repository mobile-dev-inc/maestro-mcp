#!/bin/bash
set -e

# Clean up previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Check the distribution
python -m twine check dist/*

echo "Build successful! To publish to PyPI, run:"
echo "python -m twine upload dist/*"
echo ""
echo "To publish to TestPyPI first (recommended), run:"
echo "python -m twine upload --repository testpypi dist/*"
