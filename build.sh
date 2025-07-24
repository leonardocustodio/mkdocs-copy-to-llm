#!/bin/bash
# Build script for mkdocs-copy-to-llm plugin

echo "Building mkdocs-copy-to-llm package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Install build tools if not present
pip install --upgrade pip build twine

# Build the package
python -m build

# Check the package
echo "Checking package with twine..."
twine check dist/*

echo "Build complete! Packages are in the dist/ directory."
echo ""
echo "To upload to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "To upload to TestPyPI:"
echo "  twine upload --repository testpypi dist/*"